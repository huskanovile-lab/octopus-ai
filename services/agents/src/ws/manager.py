from collections import defaultdict

from fastapi import WebSocket


class WSManager:
    def __init__(self) -> None:
        self.channels: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, channel: str, socket: WebSocket) -> None:
        await socket.accept()
        self.channels[channel].add(socket)

    def disconnect(self, channel: str, socket: WebSocket) -> None:
        self.channels[channel].discard(socket)

    async def broadcast(self, channel: str, message: dict) -> None:
        dead = []
        for socket in self.channels[channel]:
            try:
                await socket.send_json(message)
            except Exception:
                dead.append(socket)
        for socket in dead:
            self.disconnect(channel, socket)


SUPPORTED_CHANNELS = {
    "market_stream",
    "agent_activity",
    "signal_funnel",
    "rejected_signals",
    "order_updates",
    "positions",
    "portfolio_updates",
    "risk_alerts",
    "anomalies",
    "governance_state",
    "system_timeline",
    "knowledge_updates",
}
