from datetime import date


def generate_daily_operating_report(payload: dict) -> dict:
    return {
        "date": str(date.today()),
        "top_successful_conditions": payload.get("top_successful_conditions", []),
        "top_failed_conditions": payload.get("top_failed_conditions", []),
        "strategy_ranking_changes": payload.get("strategy_ranking_changes", []),
        "symbol_tradeability_changes": payload.get("symbol_tradeability_changes", []),
        "anomalies": payload.get("anomalies", []),
        "recommended_governance_mode": payload.get("recommended_governance_mode", "defensive_mode"),
    }
