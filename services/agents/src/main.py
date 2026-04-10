import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket

from .event_bus import InMemoryEventBus
from .orchestrator import AutonomousOrchestrator
from .routers.api import router as api_router
from .ws.manager import SUPPORTED_CHANNELS, WSManager

bus = InMemoryEventBus()
ws = WSManager()
orchestrator = AutonomousOrchestrator(bus)


async def fanout(channel: str, payload: dict) -> None:
    await ws.broadcast(channel, payload)


for evt, channel in {
    "market_tick_received": "market_stream",
    "signal_proposed": "signal_funnel",
    "signal_rejected": "rejected_signals",
    "order_created": "order_updates",
    "anomaly_detected": "anomalies",
}.items():
    bus.subscribe(evt, lambda payload, ch=channel: fanout(ch, payload))


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(orchestrator.start())
    yield
    await orchestrator.stop()
    task.cancel()


app = FastAPI(title="Octopus AI Agents", lifespan=lifespan)
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
