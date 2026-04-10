from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


from services.feature_engine.src.features import compute_feature_snapshot
from services.feature_engine.src.tradeability import score_tradeability
from services.governance.src.risk_engine import RiskState, evaluate_signal
from services.execution_sim.src.simulator import Order, simulate_lifecycle

from .db import Database
from .event_bus import InMemoryEventBus


@dataclass
class RuntimeState:
    symbol: str = "AAPL"
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
    def __init__(self, bus: InMemoryEventBus, db: Database) -> None:
        self.bus = bus
        self.db = db
        self.state = RuntimeState()
        self.risk = RiskState()
        self.feed = [100, 101, 102, 101, 100, 99, 100, 101, 103, 104]
        self.index = 0
        self.running = False

    async def start(self) -> None:
        self.running = True
        while self.running:
            await self.run_step()
            await asyncio.sleep(0.5)

    async def stop(self) -> None:
        self.running = False

    async def run_step(self) -> dict:
        price = self.feed[self.index % len(self.feed)]
        self.index += 1
        ts = datetime.now(UTC).isoformat()
        await self._emit("market_tick_received", {"symbol": self.state.symbol, "price": price, "ts": ts})

        regime = "trend" if self.index > 3 and price >= self.feed[(self.index - 2) % len(self.feed)] else "mean_revert"
        self.state.regime = regime
        await self._emit("regime_updated", {"symbol": self.state.symbol, "regime": regime})

        rows = [{"open": p, "high": p + 0.3, "low": p - 0.3, "close": p, "volume": 1_000 + i * 10} for i, p in enumerate(self.feed[: max(5, self.index)])]
        features = compute_feature_snapshot(rows)
        await self._emit("feature_snapshot_created", {"symbol": self.state.symbol, "features": features})

        tradeability = score_tradeability(8.0 if regime == "trend" else 24.0, 0.8, 0.7, 0.2, 0.2, 0.9, 0.85, False)
        await self._emit("tradeability_score_updated", {"symbol": self.state.symbol, **tradeability})

        signal_id = str(uuid4())
        signal = {"id": signal_id, "symbol": self.state.symbol, "strategy": "momentum", "side": "buy", "entry": price}
        self.state.signal_funnel["proposed"] += 1
        await self._emit("signal_proposed", signal)

        reasons = list(tradeability["reject_reasons"])
        ok, risk_reasons = evaluate_signal(
            self.risk,
            {
                "open_positions": 1 if self.state.position_qty else 0,
                "symbol_exposure": 0.1,
                "gross_exposure": 0.2,
                "daily_drawdown": -0.005,
                "spread_bps": 8.0 if regime == "trend" else 24.0,
                "consecutive_losses": 0,
            },
        )
        reasons.extend(risk_reasons)

        if reasons or not ok:
            self.state.signal_funnel["rejected"] += 1
            await self._emit("signal_rejected", {**signal, "reasons": sorted(set(reasons))})
            self._persist_signal(signal, "rejected", reasons)
            return {"status": "rejected", "reasons": reasons}

        self.state.signal_funnel["approved"] += 1
        await self._emit("signal_approved", signal)
        self._persist_signal(signal, "approved", [])

        order_id = str(uuid4())
        lifecycle = simulate_lifecycle(Order(symbol=self.state.symbol, side="buy", qty=10, order_type="market"), mid_price=price, spread_bps=8.0, seed=self.index)
        order_created = {"id": order_id, "signal_id": signal_id, "symbol": self.state.symbol, "qty": 10, "status": "accepted"}
        await self._emit("order_created", order_created)
        with self.db.connect() as conn:
            conn.execute("INSERT OR REPLACE INTO orders(id,signal_id,ts,status,qty,symbol) VALUES(?,?,?,?,?,?)", (order_id, signal_id, ts, "accepted", 10, self.state.symbol))

        for fill in lifecycle[1:]:
            await self._emit("order_filled", {"order_id": order_id, **fill})
            self._persist_fill(order_id, fill, ts)
            self._apply_fill(fill["qty"], fill["price"])

        self._snapshot_portfolio(ts, price)
        await self._emit("knowledge_conclusion_created", {"conclusion": f"{regime} regime favors momentum", "confidence": 0.72})
        if self.index % 6 == 0:
            await self._emit("anomaly_detected", {"anomaly_type": "volatility_spike", "detail": "Spread widened transiently"})
        await self._emit("pnl_updated", {"equity": self.state.equity, "realized_pnl": self.state.realized_pnl, "unrealized_pnl": self.state.unrealized_pnl})
        return {"status": "approved", "fills": lifecycle[1:]}

    async def _emit(self, event_name: str, payload: dict) -> None:
        ts = datetime.now(UTC).isoformat()
        self.db.insert_event(ts, event_name, payload)
        if event_name == "knowledge_conclusion_created":
            with self.db.connect() as conn:
                conn.execute("INSERT INTO knowledge_conclusions(ts,conclusion,confidence) VALUES(?,?,?)", (ts, payload.get("conclusion"), payload.get("confidence", 0.5)))
        if event_name == "anomaly_detected":
            with self.db.connect() as conn:
                conn.execute("INSERT INTO anomalies(ts,anomaly_type,detail) VALUES(?,?,?)", (ts, payload.get("anomaly_type","unknown"), payload.get("detail","")))
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

    def replay_completed_cycle(self) -> list[dict]:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT ts,event_name,payload FROM system_events WHERE event_name IN ('signal_proposed','signal_approved','order_created','order_filled','pnl_updated') ORDER BY id LIMIT 20"
            ).fetchall()
        return [{"ts": r["ts"], "event": r["event_name"], "payload": json.loads(r["payload"])} for r in rows]
