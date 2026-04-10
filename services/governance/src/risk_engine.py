from dataclasses import dataclass


@dataclass
class RiskState:
    max_daily_drawdown: float = 0.03
    max_open_positions: int = 8
    max_symbol_exposure: float = 0.20
    max_gross_exposure: float = 1.5
    consecutive_losses_limit: int = 4
    cooldown_active: bool = False
    emergency_pause: bool = False


def evaluate_signal(risk: RiskState, context: dict) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if risk.emergency_pause:
        reasons.append("global_emergency_pause")
    if context.get("open_positions", 0) >= risk.max_open_positions:
        reasons.append("max_open_positions")
    if context.get("symbol_exposure", 0.0) > risk.max_symbol_exposure:
        reasons.append("max_symbol_exposure")
    if context.get("gross_exposure", 0.0) > risk.max_gross_exposure:
        reasons.append("max_gross_exposure")
    if context.get("daily_drawdown", 0.0) < -risk.max_daily_drawdown:
        reasons.append("max_daily_drawdown")
    if context.get("spread_bps", 0.0) > 20:
        reasons.append("spread_liquidity_rejection")
    if context.get("consecutive_losses", 0) >= risk.consecutive_losses_limit:
        reasons.append("consecutive_loss_protection")
    if risk.cooldown_active:
        reasons.append("cooldown_after_losses")

    return (len(reasons) == 0, reasons)
