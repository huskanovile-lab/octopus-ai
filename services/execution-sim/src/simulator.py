from dataclasses import dataclass
from random import random


@dataclass
class Order:
    symbol: str
    side: str
    qty: int
    order_type: str  # market | limit
    limit_price: float | None = None


@dataclass
class FillResult:
    status: str
    filled_qty: int
    avg_price: float
    fee: float
    slippage_bps: float
    fill_realism_score: float


def simulate_fill(order: Order, mid_price: float, spread_bps: float, latency_ms: int = 75) -> FillResult:
    crossing_cost = spread_bps / 10000 * mid_price * (1 if order.order_type == "market" else 0.4)
    slippage_bps = max(0.1, spread_bps * (0.15 + random() * 0.35))
    slip_cost = slippage_bps / 10000 * mid_price

    partial = random() < 0.25
    filled_qty = max(1, int(order.qty * (0.4 + random() * 0.5))) if partial else order.qty

    avg_price = mid_price + crossing_cost + slip_cost if order.side == "buy" else mid_price - crossing_cost - slip_cost
    fee = 0.0005 * filled_qty * avg_price
    realism = max(0.0, min(1.0, 1.0 - (abs(latency_ms - 80) / 400) - (slippage_bps / 100)))

    return FillResult(
        status="partially_filled" if partial else "filled",
        filled_qty=filled_qty,
        avg_price=round(avg_price, 4),
        fee=round(fee, 4),
        slippage_bps=round(slippage_bps, 2),
        fill_realism_score=round(realism, 3),
    )
