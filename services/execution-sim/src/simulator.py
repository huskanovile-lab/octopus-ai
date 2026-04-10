from dataclasses import dataclass
import random


SIDE_ALIASES = {
    "buy": "buy",
    "long": "buy",
    "sell": "sell",
    "short": "sell",
}


@dataclass
class Order:
    symbol: str
    side: str
    qty: int
    order_type: str
    limit_price: float | None = None


def simulate_lifecycle(order: Order, mid_price: float, spread_bps: float, seed: int = 1) -> list[dict]:
    rng = random.Random(seed)
    canonical_side = _canonicalize_side(order.side)
    events: list[dict] = [{"status": "accepted", "qty": 0, "price": mid_price, "fee": 0.0, "slippage_bps": 0.0, "fill_realism_score": 1.0}]

    if order.order_type == "limit" and order.limit_price is not None:
        executable = order.limit_price >= mid_price if canonical_side == "buy" else order.limit_price <= mid_price
        if not executable:
            events.append({"status": "cancelled", "qty": 0, "price": mid_price, "fee": 0.0, "slippage_bps": 0.0, "fill_realism_score": 0.95})
            return events

    partial = rng.random() < 0.6
    if partial:
        first_qty = max(1, int(order.qty * 0.6))
        events.append(_fill_event("partially_filled", first_qty, canonical_side, mid_price, spread_bps, rng))
        remain = order.qty - first_qty
        if remain > 0:
            events.append(_fill_event("filled", remain, canonical_side, mid_price, spread_bps, rng))
    else:
        events.append(_fill_event("filled", order.qty, canonical_side, mid_price, spread_bps, rng))
    return events


def _canonicalize_side(side: str) -> str:
    normalized = SIDE_ALIASES.get(side.strip().lower())
    if normalized is None:
        raise ValueError(f"Unsupported order side '{side}'. Expected one of: {', '.join(SIDE_ALIASES)}")
    return normalized


def _fill_event(status: str, qty: int, side: str, mid_price: float, spread_bps: float, rng: random.Random) -> dict:
    slippage_bps = round(spread_bps * (0.1 + rng.random() * 0.25), 3)
    direction = 1 if side == "buy" else -1
    px = mid_price + direction * (slippage_bps / 10000 * mid_price)
    fee = round(px * qty * 0.0005, 4)
    realism = round(max(0.0, 1.0 - slippage_bps / 100), 3)
    return {
        "status": status,
        "qty": qty,
        "price": round(px, 4),
        "fee": fee,
        "slippage_bps": slippage_bps,
        "fill_realism_score": realism,
    }
