# File-by-file Scaffold Plan

## Apps
- `apps/web/app/page.tsx` — Control room homepage.
- `apps/web/components/control-room.tsx` — Glassmorphism dashboard skeleton.
- `apps/web/package.json` — Next.js scripts.

## Shared packages
- `packages/shared-types/src/events.ts` — Event and confidence contracts.
- `packages/shared-types/src/index.ts` — Exports.
- `packages/shared-config/src/runtime.py` — Environment settings.

## Services / agents
- `services/agents/src/main.py` — FastAPI entry.
- `services/agents/src/orchestrator.py` — Always-on autonomous loop.
- `services/agents/src/event_bus.py` — In-memory async bus (Redis-ready boundary).
- `services/agents/src/models.py` — Pydantic API/event models.
- `services/agents/src/routers/*.py` — Required REST endpoints.
- `services/agents/src/ws/manager.py` — WS fanout channel manager.

## Services / feature-engine
- `services/feature-engine/src/features.py` — Feature computations.
- `services/feature-engine/src/tradeability.py` — Tradeability score with reasons.

## Services / execution-sim
- `services/execution-sim/src/simulator.py` — Realistic paper fill simulation.

## Services / governance
- `services/governance/src/risk_engine.py` — Risk checks and gates.
- `services/governance/src/health.py` — System health tracking.

## Services / research
- `services/research/src/daily_report.py` — Automatic daily operating report.

## Infrastructure
- `infrastructure/postgres/schema.sql` — Core schema.
- `infrastructure/docker-compose.yml` — Postgres + Redis local stack.
