from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from services.execution_sim.src.simulator import Order, simulate_lifecycle
from services.feature_engine.src.features import compute_feature_snapshot
from services.feature_engine.src.tradeability import score_tradeability
from services.governance.src.risk_engine import RiskState, evaluate_signal

from .db import Database
from .event_bus import InMemoryEventBus
from .feed_adapter import DeterministicDemoFeed, MarketDataAdapter
from .knowledge import build_knowledge_conclusion
from .observability import Observability
from .replay import reconstruct_decision_chain

logger = logging.getLogger("autonomous_runtime")

AUTONOMY_MODES = {
    "observer_mode",
    "supervised_paper_mode",
    "autonomous_paper_mode",
    "defensive_mode",
    "paused_mode",
}


@dataclass
class RuntimeState:
    symbol: str = "AAPL"
    mode: str = "autonomous_paper_mode"
    cash: float = 100_000.0
    equity: float = 100_000.0
    position_qty: int = 0
    avg_price: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    regime: str = "unknown"
    active: bool = True
    signal_funnel: dict = field(default_factory=lambda: {"proposed": 0, "rejected": 0, "approved": 0})


class AutonomousRuntime:
    def __init__(self, bus: InMemoryEventBus, db: Database, adapter: MarketDataAdapter | None = None) -> None:
        self.bus = bus
        self.db = db
        self.state = RuntimeState()
        self.risk = RiskState()
        self.adapter = adapter or DeterministicDemoFeed(symbol=self.state.symbol)
        self.index = 0
        self.running = False
        self.obs = Observability()

    async def start(self) -> None:
        self.running = True
        while self.running:
            await self.run_step()
            await asyncio.sleep(0.5)

    async def stop(self) -> None:
        self.running = False

    def set_mode(self, mode: str) -> None:
        if mode not in AUTONOMY_MODES:
            raise ValueError(f"unknown mode: {mode}")
        self.state.mode = mode
        self.state.active = mode != "paused_mode"

    async def run_step(self) -> dict:
        self.obs.tick_heartbeat()
        loop_start = perf_counter()
        ts = datetime.now(UTC).isoformat()

        if self.state.mode == "paused_mode":
            await self._emit("heartbeat", {"ts": ts, "mode": self.state.mode})
            self.obs.time_stage("paused", loop_start)
            self._log_stage("paused", {"mode": self.state.mode})
            return {"status": "paused"}

        t0 = perf_counter()
        tick = self.adapter.next_tick()
        self.index += 1
        await self._emit("market_tick_received", {"symbol": tick.symbol, "price": tick.price, "volume": tick.volume, "spread_bps": tick.spread_bps, "ts": ts})
        self.obs.time_stage("observe", t0)

        t1 = perf_counter()
        regime = "trend" if self.index > 2 and tick.price >= 100 else "mean_revert"
        self.state.regime = regime
        await self._emit("regime_updated", {"symbol": self.state.symbol, "regime": regime})

        rows = [
            {"open": 100 + i * 0.1, "high": 100.3 + i * 0.1, "low": 99.7 + i * 0.1, "close": 100 + i * 0.1, "volume": 1_000 + i * 10}
            for i in range(max(20, self.index + 1))
        ]
        rows[-1]["close"] = tick.price
        rows[-1]["high"] = tick.price + 0.3
        rows[-1]["low"] = tick.price - 0.3
        features = compute_feature_snapshot(rows)
        await self._emit("feature_snapshot_created", {"symbol": self.state.symbol, "features": features})

        tradeability = score_tradeability(
            spread_bps=tick.spread_bps,
            liquidity_score=0.8,
            vol_suitability=0.7,
            chop_score=0.25 if regime == "mean_revert" else 0.12,
            false_breakout_risk=0.2,
            session_suitability=0.9,
            execution_realism=0.88,
            anomaly_flag=False,
        )
        await self._emit("tradeability_score_updated", {"symbol": self.state.symbol, **tradeability})
        self.obs.time_stage("understand", t1)

        t2 = perf_counter()
        signal_id = str(uuid4())
        signal = {"id": signal_id, "symbol": self.state.symbol, "strategy": "momentum", "side": "buy", "entry": tick.price}
        self.state.signal_funnel["proposed"] += 1
        await self._emit("signal_proposed", signal)

        reasons = list(tradeability["reject_reasons"])
        spread_threshold = 10.0 if self.state.mode == "defensive_mode" else 20.0
        ok, risk_reasons = evaluate_signal(
            self.risk,
            {
                "open_positions": 1 if self.state.position_qty else 0,
                "symbol_exposure": 0.1,
                "gross_exposure": 0.2,
                "daily_drawdown": -0.005,
                "spread_bps": tick.spread_bps if tick.spread_bps > spread_threshold else 0.0,
                "consecutive_losses": 0,
            },
        )
        reasons.extend(risk_reasons)

        if self.state.mode in {"observer_mode", "supervised_paper_mode"}:
            reasons.append("mode_blocks_execution")

        if reasons or not ok:
            uniq = sorted(set(reasons))
            self.obs.count_rejections(uniq)
            self.state.signal_funnel["rejected"] += 1
            await self._emit("signal_rejected", {**signal, "reasons": uniq})
            self._persist_signal(signal, "rejected", uniq)
            self.obs.time_stage("decide", t2)
            self._log_stage("decide", {"decision": "reject", "reasons": uniq, "mode": self.state.mode})
            return {"status": "rejected", "reasons": uniq}

        self.state.signal_funnel["approved"] += 1
        await self._emit("signal_approved", signal)
        self._persist_signal(signal, "approved", [])
        self.obs.time_stage("decide", t2)

        t3 = perf_counter()
        qty = 5 if self.state.mode == "defensive_mode" else 10
        order_id = str(uuid4())
        lifecycle = simulate_lifecycle(
            Order(symbol=self.state.symbol, side="buy", qty=qty, order_type="market"),
            mid_price=tick.price,
            spread_bps=tick.spread_bps,
            seed=self.index,
        )
        self.obs.count_order()

        await self._emit("order_created", {"id": order_id, "signal_id": signal_id, "symbol": self.state.symbol, "qty": qty, "status": lifecycle[0]["status"]})
        with self.db.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO orders(id,signal_id,ts,status,qty,symbol) VALUES(?,?,?,?,?,?)",
                (order_id, signal_id, ts, lifecycle[0]["status"], qty, self.state.symbol),
            )

        for fill in lifecycle[1:]:
            await self._emit("order_filled", {"order_id": order_id, **fill})
            self.obs.count_fill(fill["status"], fill["slippage_bps"], fill["fill_realism_score"])
            self._persist_fill(order_id, fill, ts)
            self._apply_fill(fill["qty"], fill["price"])

        self._snapshot_portfolio(ts, tick.price)
        self.obs.time_stage("act", t3)

        t4 = perf_counter()
        k = build_knowledge_conclusion(self.state.symbol, regime, features, tradeability["tradeability_score"])
        await self._emit(
            "knowledge_conclusion_created",
            {"conclusion": k.conclusion, "evidence": k.evidence, "confidence": k.confidence, "stale_after_ts": k.stale_after_ts},
        )
        if self.index % 6 == 0:
            await self._emit("anomaly_detected", {"anomaly_type": "volatility_spike", "detail": "Spread widened transiently"})
            self.obs.count_anomaly("volatility_spike")
        await self._emit("pnl_updated", {"equity": self.state.equity, "realized_pnl": self.state.realized_pnl, "unrealized_pnl": self.state.unrealized_pnl})
        self.obs.time_stage("review_adapt", t4)
        self.obs.time_stage("loop_total", loop_start)

        self._log_stage(
            "loop_summary",
            {
                "mode": self.state.mode,
                "regime": regime,
                "price": tick.price,
                "funnel": self.state.signal_funnel,
                "metrics": self.obs.snapshot(),
            },
        )
        return {"status": "approved", "fills": lifecycle[1:]}

    async def _emit(self, event_name: str, payload: dict) -> None:
        ts = datetime.now(UTC).isoformat()
        self.db.insert_event(ts, event_name, payload)
        self.obs.count_event(event_name)
        if event_name == "knowledge_conclusion_created":
            with self.db.connect() as conn:
                conn.execute(
                    "INSERT INTO knowledge_conclusions(ts,conclusion,evidence,confidence,stale_after_ts,status) VALUES(?,?,?,?,?,?)",
                    (ts, payload.get("conclusion"), json.dumps(payload.get("evidence", {})), payload.get("confidence", 0.5), payload.get("stale_after_ts"), "active"),
                )
        if event_name == "anomaly_detected":
            with self.db.connect() as conn:
                conn.execute(
                    "INSERT INTO anomalies(ts,anomaly_type,detail) VALUES(?,?,?)",
                    (ts, payload.get("anomaly_type", "unknown"), payload.get("detail", "")),
                )
        await self.bus.publish(event_name, payload)

    def _persist_signal(self, signal: dict, status: str, reasons: list[str]) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO signals(id,ts,symbol,strategy,side,status,reasons,confidence) VALUES(?,?,?,?,?,?,?,?)",
                (signal["id"], datetime.now(UTC).isoformat(), signal["symbol"], signal["strategy"], signal["side"], status, json.dumps(reasons), 0.7),
            )

    def _persist_fill(self, order_id: str, fill: dict, ts: str) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO fills(order_id,ts,status,qty,price,fee,slippage_bps,realism) VALUES(?,?,?,?,?,?,?,?)",
                (order_id, ts, fill["status"], fill["qty"], fill["price"], fill["fee"], fill["slippage_bps"], fill["fill_realism_score"]),
            )

    def _apply_fill(self, qty: int, price: float) -> None:
        new_qty = self.state.position_qty + qty
        self.state.avg_price = ((self.state.avg_price * self.state.position_qty) + qty * price) / max(new_qty, 1)
        self.state.position_qty = new_qty
        self.state.cash -= qty * price

    def _snapshot_portfolio(self, ts: str, mark: float) -> None:
        self.state.unrealized_pnl = (mark - self.state.avg_price) * self.state.position_qty
        self.state.equity = self.state.cash + self.state.position_qty * mark
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO portfolio_snapshots(ts,equity,cash,unrealized_pnl,realized_pnl) VALUES(?,?,?,?,?)",
                (ts, self.state.equity, self.state.cash, self.state.unrealized_pnl, self.state.realized_pnl),
            )
            conn.execute(
                "INSERT OR REPLACE INTO positions(symbol,qty,avg_price,unrealized_pnl,realized_pnl,updated_at) VALUES(?,?,?,?,?,?)",
                (self.state.symbol, self.state.position_qty, self.state.avg_price, self.state.unrealized_pnl, self.state.realized_pnl, ts),
            )

    def replay_completed_cycle(self) -> dict:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT ts,event_name,payload FROM system_events ORDER BY id DESC LIMIT 120"
            ).fetchall()
        ordered = list(reversed([dict(r) for r in rows]))
        chain = []
        in_chain = False
        for row in ordered:
            ev = row["event_name"]
            if ev == "signal_proposed":
                in_chain = True
                chain = [row]
                continue
            if in_chain:
                chain.append(row)
                if ev in {"signal_rejected", "pnl_updated"}:
                    break
        return reconstruct_decision_chain(chain)

    def _log_stage(self, stage: str, payload: dict) -> None:
        logger.info(json.dumps({"stage": stage, "ts": datetime.now(UTC).isoformat(), **payload}))
