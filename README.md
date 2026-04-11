# Octopus AI — Autonomous Runtime (Hardened Vertical Slice)

## Local setup (clean clone)
Backend (one command, includes seed/demo mode):
```bash
bash scripts/start_backend.sh
```
Frontend (one command):
```bash
bash scripts/start_frontend.sh
```


## Windows (CMD/PowerShell) quick start
Backend:
```bat
scripts\start_backend_windows.bat
```
Frontend (new terminal):
```bat
scripts\start_frontend_windows.bat
```
If you see `'bash' is not recognized`, use these `.bat` scripts instead of `.sh`.


## Windows troubleshooting
If you see:
- `'bash' is not recognized` -> use `.bat` scripts.
- `Failed building wheel for pydantic-core` or `No module named 'fastapi'` -> install/use **Python 3.12** and rerun `scripts\start_backend_windows.bat`.
- Next.js warnings about missing layout or allowed dev origins are already handled in this repo (`app/layout.tsx`, `next.config.ts`).

## Concise architecture
- `services/agents/src/runtime.py`: always-on autonomous loop with autonomy modes.
- `services/agents/src/feed_adapter.py`: market data adapter boundary (`DeterministicDemoFeed` for verification).
- `services/agents/src/db.py`: persisted events/signals/orders/fills/positions/knowledge/anomalies.
- `services/agents/src/observability.py`: heartbeat, stage timing, event/rejection/execution/anomaly metrics.
- `services/agents/src/replay.py`: decision-chain reconstruction + replay invariants.
- `apps/web/components/control-room.tsx`: live state + grouped timeline + mode controls.

## Runtime walkthrough
Each loop step performs:
1. Observe: ingest deterministic tick and emit `market_tick_received`.
2. Understand: compute features + regime + tradeability.
3. Decide: propose signal and either reject (stored reasons) or approve.
4. Act: simulate order lifecycle and update positions/portfolio.
5. Review/Adapt: emit PnL, knowledge conclusion (with evidence/confidence/staleness), anomalies.
6. Observe itself: structured logs + stage timings + heartbeat/event counters.

## How to verify the autonomous system is alive
- Check runtime status and mode:
  - `curl http://localhost:8000/api/v1/system/status`
- Check observability metrics:
  - `curl http://localhost:8000/api/v1/system/metrics`
- Check decision funnel:
  - `curl http://localhost:8000/api/v1/signals`
  - `curl http://localhost:8000/api/v1/signals/rejected`
- Check execution/portfolio:
  - `curl http://localhost:8000/api/v1/fills`
  - `curl http://localhost:8000/api/v1/positions`
  - `curl http://localhost:8000/api/v1/portfolio/state`
- Check deterministic replay chain + invariants:
  - `curl http://localhost:8000/api/v1/replay/example`

## Replay invariants
A valid reconstructed decision chain must include:
- ordered prefix: `market_tick_received -> regime_updated -> feature_snapshot_created -> tradeability_score_updated -> signal_proposed`
- terminal decision:
  - either `signal_rejected`,
  - or `signal_approved` followed by `order_created`, `order_filled`, `pnl_updated`.

## Known limitations
- Single symbol and deterministic feed only (real feed adapter interface exists but adapter not yet implemented).
- Simplified position model (long-only accumulation for demo).
- SQLite local persistence for verification; production Postgres path remains separate.
- Frontend optimized for inspection over polish.

## Tests
```bash
pytest -q
```

## Downloadable project bundle
Create downloadable archives:
```bash
bash scripts/create_download_bundle.sh
```
Outputs go to `dist/` as `.zip` and `.tar.gz`.


Optional curated release package:
```bash
bash scripts/create_release_folder.sh
```
Creates `dist/release-package/` and `dist/release-package.zip`.


Named export bundle (example):
```bash
bash scripts/create_named_bundle.sh Gbg-codex-trading-ready
```
Creates `dist/Gbg-codex-trading-ready.zip`.
