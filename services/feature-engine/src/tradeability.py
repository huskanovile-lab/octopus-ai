def score_tradeability(
    spread_bps: float,
    liquidity_score: float,
    vol_suitability: float,
    chop_score: float,
    false_breakout_risk: float,
    session_suitability: float,
    execution_realism: float,
    anomaly_flag: bool,
) -> dict:
    penalties = 0.0
    penalties += min(spread_bps / 25.0, 1.0) * 0.25
    penalties += (1 - liquidity_score) * 0.20
    penalties += (1 - vol_suitability) * 0.15
    penalties += chop_score * 0.10
    penalties += false_breakout_risk * 0.10
    penalties += (1 - session_suitability) * 0.10
    penalties += (1 - execution_realism) * 0.10
    penalties += 0.15 if anomaly_flag else 0.0

    score = max(0.0, min(1.0, 1 - penalties))
    reasons = []
    if spread_bps > 20:
        reasons.append("spread_too_wide")
    if liquidity_score < 0.4:
        reasons.append("low_liquidity")
    if anomaly_flag:
        reasons.append("anomaly_active")

    return {"tradeability_score": score, "reject_reasons": reasons}
