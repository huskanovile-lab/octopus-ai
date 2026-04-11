from services.feature_engine.src.tradeability import score_tradeability


def test_tradeability_rejects_wide_spread():
    out = score_tradeability(30, 0.9, 0.8, 0.2, 0.1, 0.8, 0.9, False)
    assert out["tradeability_score"] < 0.8
    assert "spread_too_wide" in out["reject_reasons"]
