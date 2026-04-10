from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")


@router.get("/symbols")
async def symbols():
    return [{"symbol": "AAPL"}, {"symbol": "MSFT"}]


@router.get("/strategies")
async def strategies():
    return {
        "active": ["momentum", "mean_reversion", "breakout"],
        "shadow": ["breakout_v2_shadow"],
        "paused": [],
    }


@router.get("/agents/status")
async def agent_status():
    return {"status": "running", "agents": 12}


@router.get("/signals")
async def signals():
    return []


@router.get("/signals/rejected")
async def rejected_signals():
    return []


@router.get("/orders")
async def orders():
    return []


@router.get("/fills")
async def fills():
    return []


@router.get("/positions")
async def positions():
    return []


@router.get("/portfolio/state")
async def portfolio_state():
    return {"equity": 100000, "drawdown": 0.0}


@router.get("/risk/state")
async def risk_state():
    return {"mode": "normal", "risk_multiplier": 1.0}


@router.get("/governance/mode")
async def governance_mode():
    return {"mode": "autonomous_paper_mode"}


@router.get("/anomalies")
async def anomalies():
    return []


@router.get("/experiments")
async def experiments():
    return []


@router.get("/knowledge/conclusions")
async def knowledge_conclusions():
    return []


@router.get("/daily-summaries")
async def daily_summaries():
    return []


@router.get("/replay/sessions")
async def replay_sessions():
    return []


@router.get("/system/events")
async def system_events():
    return []


@router.get("/system/health")
async def system_health():
    return {
        "data_feed_quality": 0.98,
        "agent_responsiveness": 0.99,
        "signal_spam": 0.06,
        "execution_realism_drift": 0.04,
        "strategy_degradation": 0.10,
        "anomaly_pressure": 0.09,
    }
