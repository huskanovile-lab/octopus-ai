import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket

from .db import Database
from .event_bus import InMemoryEventBus
from .routers.api import router as api_router
from .runtime import AutonomousRuntime
from .ws.manager import SUPPORTED_CHANNELS, WSManager

logging.basicConfig(level=logging.INFO, format="%(message)s")


def build_app(start_loop: bool = True) -> FastAPI:
    bus = InMemoryEventBus()
    ws = WSManager()
    db = Database(path=os.getenv("DEMO_DB_PATH", "services/agents/demo.db"))
    runtime = AutonomousRuntime(bus, db)

    async def fanout(channel: str, payload: dict) -> None:
        await ws.broadcast(channel, payload)

    mapping = {
        "market_tick_received": "market_stream",
        "regime_updated": "agent_activity",
        "signal_proposed": "signal_funnel",
        "signal_rejected": "rejected_signals",
        "signal_approved": "signal_funnel",
        "order_created": "order_updates",
        "order_filled": "order_updates",
        "pnl_updated": "portfolio_updates",
        "anomaly_detected": "anomalies",
        "knowledge_conclusion_created": "knowledge_updates",
        "heartbeat": "agent_activity",
    }
    for evt, channel in mapping.items():
        bus.subscribe(evt, lambda payload, ch=channel: fanout(ch, payload))
        bus.subscribe(evt, lambda payload, ev=evt: fanout("system_timeline", {"event": ev, "payload": payload}))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        task = None
        if start_loop:
            task = asyncio.create_task(runtime.start())
        yield
        await runtime.stop()
        if task:
            task.cancel()

    app = FastAPI(title="Octopus AI Agents", lifespan=lifespan)
    app.state.db = db
    app.state.runtime = runtime
    app.include_router(api_router)

    @app.websocket("/ws/{channel}")
    async def websocket_channel(socket: WebSocket, channel: str):
        if channel not in SUPPORTED_CHANNELS:
            await socket.close(code=1008)
            return
        await ws.connect(channel, socket)
        try:
            while True:
                await socket.receive_text()
        except Exception:
            ws.disconnect(channel, socket)

    return app


app = build_app(start_loop=os.getenv("DISABLE_AUTO_LOOP", "0") != "1")
