from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MarketTick:
    symbol: str
    price: float
    volume: float
    spread_bps: float


class MarketDataAdapter:
    """Boundary interface for market feeds (demo or real adapters)."""

    def next_tick(self) -> MarketTick:  # pragma: no cover - interface
        raise NotImplementedError


class DeterministicDemoFeed(MarketDataAdapter):
    def __init__(self, symbol: str = "AAPL") -> None:
        self.symbol = symbol
        self._prices = [100, 101, 102, 101, 100, 99, 100, 101, 103, 104]
        self._spreads = [24, 22, 8, 7, 6, 5, 10, 9, 8, 7]
        self._idx = 0

    def next_tick(self) -> MarketTick:
        i = self._idx % len(self._prices)
        self._idx += 1
        return MarketTick(
            symbol=self.symbol,
            price=float(self._prices[i]),
            volume=1_000 + i * 25,
            spread_bps=float(self._spreads[i]),
        )
