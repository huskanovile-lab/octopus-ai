from services.governance.src.risk_engine import RiskState, evaluate_signal


def test_risk_rejects_drawdown_and_spread():
    ok, reasons = evaluate_signal(RiskState(), {"daily_drawdown": -0.04, "spread_bps": 25})
    assert not ok
    assert "max_daily_drawdown" in reasons
    assert "spread_liquidity_rejection" in reasons
