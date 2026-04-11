from __future__ import annotations

import json
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")


class ModeUpdate(BaseModel):
    mode: str


@router.get("/system/status")
async def system_status(request: Request):
    s = request.app.state.runtime.state
    return {"ai_active": s.active, "regime": s.regime, "symbol": s.symbol, "mode": s.mode, "signal_funnel": s.signal_funnel}


@router.get("/system/metrics")
async def system_metrics(request: Request):
    return request.app.state.runtime.obs.snapshot()


@router.post("/system/mode")
async def set_mode(body: ModeUpdate, request: Request):
    try:
        request.app.state.runtime.set_mode(body.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"mode": request.app.state.runtime.state.mode}


@router.post("/demo/run-step")
async def run_step(request: Request):
    return await request.app.state.runtime.run_step()


@router.get("/signals")
async def signals(request: Request):
    with request.app.state.db.connect() as conn:
        rows = conn.execute("SELECT * FROM signals ORDER BY ts DESC LIMIT 25").fetchall()
    return [dict(r) for r in rows]


@router.get("/signals/rejected")
async def rejected_signals(request: Request):
    with request.app.state.db.connect() as conn:
        rows = conn.execute("SELECT * FROM signals WHERE status='rejected' ORDER BY ts DESC LIMIT 25").fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["reasons"] = json.loads(item["reasons"] or "[]")
        out.append(item)
    return out


@router.get("/orders")
async def orders(request: Request):
    with request.app.state.db.connect() as conn:
        rows = conn.execute("SELECT * FROM orders ORDER BY ts DESC LIMIT 25").fetchall()
    return [dict(r) for r in rows]


@router.get("/fills")
async def fills(request: Request):
    with request.app.state.db.connect() as conn:
        rows = conn.execute("SELECT * FROM fills ORDER BY id DESC LIMIT 25").fetchall()
    return [dict(r) for r in rows]


@router.get("/positions")
async def positions(request: Request):
    with request.app.state.db.connect() as conn:
        rows = conn.execute("SELECT * FROM positions").fetchall()
    return [dict(r) for r in rows]


@router.get("/portfolio/state")
async def portfolio_state(request: Request):
    s = request.app.state.runtime.state
    return {"equity": s.equity, "cash": s.cash, "unrealized_pnl": s.unrealized_pnl, "realized_pnl": s.realized_pnl}


@router.get("/knowledge/conclusions")
async def knowledge(request: Request):
    with request.app.state.db.connect() as conn:
        rows = conn.execute("SELECT * FROM knowledge_conclusions ORDER BY id DESC LIMIT 10").fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["evidence"] = json.loads(item["evidence"] or "{}")
        out.append(item)
    return out


@router.get("/anomalies")
async def anomalies(request: Request):
    with request.app.state.db.connect() as conn:
        rows = conn.execute("SELECT * FROM anomalies ORDER BY id DESC LIMIT 10").fetchall()
    return [dict(r) for r in rows]


@router.get("/system/events")
async def system_events(request: Request):
    with request.app.state.db.connect() as conn:
        rows = conn.execute("SELECT * FROM system_events ORDER BY id DESC LIMIT 100").fetchall()
    return [{**dict(r), "payload": json.loads(r["payload"])} for r in rows]


@router.get("/replay/example")
async def replay_example(request: Request):
    return request.app.state.runtime.replay_completed_cycle()
