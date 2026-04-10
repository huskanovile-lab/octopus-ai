# Octopus AI — Autonomous Paper Trading Vertical Slice

This repo now contains a **working end-to-end autonomous paper trading loop** for one symbol (`AAPL`) with deterministic market feed steps.

## What is implemented
- Autonomous loop starts automatically on API startup (`uvicorn services.agents.src.main:app --reload`).
- Deterministic feed drives: features -> regime -> signal -> tradeability -> risk -> execution -> portfolio updates.
- Weak signals are rejected with explicit reason codes and persisted.
- Approved signals pass through realistic paper order lifecycle (accepted, partially_filled/filled).
- Major events are persisted to database (`services/agents/demo.db`) and streamed over WebSockets.
- Dashboard shows live state: activity, regime, symbol, signal funnel, rejected signals, fills/positions, pnl, knowledge, anomalies.
- Deterministic replay endpoint: `/api/v1/replay/example`.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r services/agents/requirements.txt pytest
uvicorn services.agents.src.main:app --reload --port 8000
```

In another terminal:
```bash
cd apps/web
npm install
npm run dev
```
Open `http://localhost:3000`.

## Deterministic demo seed/run
```bash
python scripts/run_demo_session.py
```

## How to verify the autonomous system is alive
1. Start API and Web app as above.
2. Confirm backend auto-loop is active:
   - `curl http://localhost:8000/api/v1/system/status` should return `"ai_active": true`.
3. Observe event growth:
   - `curl http://localhost:8000/api/v1/system/events | jq 'length'` should keep increasing.
4. Confirm signal funnel behavior:
   - `curl http://localhost:8000/api/v1/signals`
   - `curl http://localhost:8000/api/v1/signals/rejected`
5. Confirm paper execution + portfolio updates:
   - `curl http://localhost:8000/api/v1/fills`
   - `curl http://localhost:8000/api/v1/positions`
   - `curl http://localhost:8000/api/v1/portfolio/state`
6. Confirm replayable trade cycle:
   - `curl http://localhost:8000/api/v1/replay/example`
7. Open dashboard and verify live updates for:
   - AI active status, current regime, watched symbol, signal funnel, rejected signals,
     approved/executed trades, open positions, portfolio pnl, latest knowledge, latest anomalies.

## Tests
```bash
pytest -q
```
