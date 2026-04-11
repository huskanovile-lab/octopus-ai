import asyncio
from collections import defaultdict
from typing import Any, Awaitable, Callable

Handler = Callable[[dict[str, Any]], Awaitable[None]]


class InMemoryEventBus:
    """Redis/Kafka boundary interface; in-memory for scaffold."""

    def __init__(self) -> None:
        self._subs: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: Handler) -> None:
        self._subs[event_name].append(handler)

    async def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        handlers = self._subs.get(event_name, [])
        if handlers:
            await asyncio.gather(*(h(payload) for h in handlers))
