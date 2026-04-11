from __future__ import annotations

import json


REPLAY_CHAIN = [
    "market_tick_received",
    "regime_updated",
    "feature_snapshot_created",
    "tradeability_score_updated",
    "signal_proposed",
]


def reconstruct_decision_chain(rows: list[dict]) -> dict:
    events = [r["event_name"] for r in rows]
    start_ok = False
    for i in range(0, max(1, len(events) - len(REPLAY_CHAIN) + 1)):
        if events[i:i+len(REPLAY_CHAIN)] == REPLAY_CHAIN:
            start_ok = True
            break
    end_ok = any(e in events for e in ["signal_rejected", "signal_approved"])
    if "signal_approved" in events:
        end_ok = end_ok and "order_created" in events and "order_filled" in events and "pnl_updated" in events

    return {
        "events": [
            {"ts": r["ts"], "event": r["event_name"], "payload": json.loads(r["payload"])}
            for r in rows
        ],
        "invariants": {
            "ordered_prefix": start_ok,
            "decision_terminal_present": end_ok,
        },
    }
