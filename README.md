# Octopus AI — Autonomous Paper Trading Operating System

Production-style monorepo scaffold for an always-on, multi-agent, event-driven AI paper trading platform.

See `docs/SYSTEM_BLUEPRINT.md` for full architecture in the requested order and `docs/FILE_SCAFFOLD_PLAN.md` for implementation map.

## Quick start

```bash
# Backend API
python -m venv .venv
source .venv/bin/activate
pip install -r services/agents/requirements.txt
uvicorn services.agents.src.main:app --reload --port 8000
```

```bash
# Frontend shell (placeholder)
cd apps/web
npm install
npm run dev
```
