import asyncio
from datetime import UTC, datetime
from random import random

from .event_bus import InMemoryEventBus


class AutonomousOrchestrator:
    def __init__(self, bus: InMemoryEventBus) -> None:
        self.bus = bus
        self.running = False
        self.mode = "autonomous_paper_mode"

    async def start(self) -> None:
        self.running = True
        while self.running:
            now = datetime.now(UTC).isoformat()
            tick = {"symbol": "AAPL", "price": 180 + random(), "ts": now}
            await self.bus.publish("market_tick_received", tick)
            await self._agent_cycle(tick)
            await asyncio.sleep(1.0)

    async def stop(self) -> None:
        self.running = False

    async def _agent_cycle(self, tick: dict) -> None:
        if self.mode == "paused_mode":
            return
        await self.bus.publish("regime_updated", {"symbol": tick["symbol"], "regime": "trend"})
        await self.bus.publish("tradeability_score_updated", {"symbol": tick["symbol"], "score": 0.82})

        signal = {
            "symbol": tick["symbol"],
            "strategy": "momentum",
            "side": "long",
            "entry": tick["price"],
        }
        await self.bus.publish("signal_proposed", signal)

        if random() > 0.45:
            await self.bus.publish("signal_approved", {**signal, "reason": "risk_ok"})
            await self.bus.publish("order_created", {"symbol": tick["symbol"], "type": "market", "qty": 10})
        else:
            await self.bus.publish(
                "signal_rejected",
                {**signal, "reasons": ["spread_too_wide", "session_noise"]},
            )
