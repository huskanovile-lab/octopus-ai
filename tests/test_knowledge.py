from datetime import UTC, datetime, timedelta

from services.agents.src.knowledge import build_knowledge_conclusion, is_stale


def test_knowledge_conclusion_contains_evidence_confidence_and_staleness():
    k = build_knowledge_conclusion(
        symbol="AAPL",
        regime="trend",
        features={"momentum_10": 0.12, "zscore_20": 1.3, "rolling_vol_20": 0.02},
        tradeability=0.81,
    )
    assert "AAPL" in k.conclusion
    assert "tradeability" in k.conclusion
    assert 0 <= k.confidence <= 1
    assert "momentum_10" in k.evidence


def test_staleness_check():
    past = (datetime.now(UTC) - timedelta(minutes=1)).isoformat()
    now = datetime.now(UTC).isoformat()
    assert is_stale(past, now)
