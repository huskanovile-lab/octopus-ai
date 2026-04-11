from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass
class KnowledgeConclusion:
    conclusion: str
    evidence: dict
    confidence: float
    stale_after_ts: str


def build_knowledge_conclusion(symbol: str, regime: str, features: dict, tradeability: float) -> KnowledgeConclusion:
    momentum = round(features.get("momentum_10", 0.0), 4)
    vol = round(features.get("rolling_vol_20", 0.0), 4)
    zscore = round(features.get("zscore_20", 0.0), 3)
    conf = max(0.1, min(0.95, 0.55 + (0.15 if regime == "trend" else -0.05) + (0.15 if tradeability > 0.7 else -0.1)))
    conclusion = (
        f"{symbol}: regime={regime}; momentum_10={momentum}; zscore_20={zscore}; "
        f"vol20={vol}; tradeability={round(tradeability, 3)}"
    )
    stale_after = datetime.now(UTC) + timedelta(minutes=10)
    return KnowledgeConclusion(
        conclusion=conclusion,
        evidence={"momentum_10": momentum, "zscore_20": zscore, "rolling_vol_20": vol, "tradeability": tradeability},
        confidence=round(conf, 3),
        stale_after_ts=stale_after.isoformat(),
    )


def is_stale(stale_after_ts: str, now_ts: str) -> bool:
    return now_ts > stale_after_ts
