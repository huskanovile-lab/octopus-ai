from dataclasses import dataclass


@dataclass
class SystemHealth:
    data_feed_quality: float
    agent_responsiveness: float
    signal_spam: float
    execution_realism_drift: float
    strategy_degradation: float
    anomaly_pressure: float


def overall_health(health: SystemHealth) -> float:
    penalties = (
        (1 - health.data_feed_quality) * 0.30
        + (1 - health.agent_responsiveness) * 0.20
        + health.signal_spam * 0.10
        + health.execution_realism_drift * 0.10
        + health.strategy_degradation * 0.20
        + health.anomaly_pressure * 0.10
    )
    return max(0.0, min(1.0, 1 - penalties))
