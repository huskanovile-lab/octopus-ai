from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from time import perf_counter


@dataclass
class Observability:
    heartbeat_count: int = 0
    loop_count: int = 0
    event_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    stage_timings_ms: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    risk_rejection_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    execution_metrics: dict[str, float] = field(
        default_factory=lambda: {"orders": 0, "fills": 0, "partial_fills": 0, "avg_slippage_bps": 0.0, "avg_realism": 0.0}
    )
    anomaly_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def tick_heartbeat(self) -> None:
        self.heartbeat_count += 1
        self.loop_count += 1

    def count_event(self, event_name: str) -> None:
        self.event_counts[event_name] += 1

    def time_stage(self, stage: str, start: float) -> None:
        self.stage_timings_ms[stage].append((perf_counter() - start) * 1000)

    def count_rejections(self, reasons: list[str]) -> None:
        for r in reasons:
            self.risk_rejection_counts[r] += 1

    def count_fill(self, status: str, slippage_bps: float, realism: float) -> None:
        m = self.execution_metrics
        m["fills"] += 1
        if status == "partially_filled":
            m["partial_fills"] += 1
        fills = max(1, m["fills"])
        m["avg_slippage_bps"] = ((m["avg_slippage_bps"] * (fills - 1)) + slippage_bps) / fills
        m["avg_realism"] = ((m["avg_realism"] * (fills - 1)) + realism) / fills

    def count_order(self) -> None:
        self.execution_metrics["orders"] += 1

    def count_anomaly(self, category: str) -> None:
        self.anomaly_counts[category] += 1

    def snapshot(self) -> dict:
        avg_stage = {
            k: (sum(v) / len(v) if v else 0.0)
            for k, v in self.stage_timings_ms.items()
        }
        return {
            "heartbeat_count": self.heartbeat_count,
            "loop_count": self.loop_count,
            "event_counts": dict(self.event_counts),
            "stage_timings_ms": avg_stage,
            "risk_rejection_counts": dict(self.risk_rejection_counts),
            "execution_metrics": self.execution_metrics,
            "anomaly_counts": dict(self.anomaly_counts),
        }
