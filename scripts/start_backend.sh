#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
source .venv/bin/activate
pip install -r services/agents/requirements.txt
python scripts/run_demo_session.py
uvicorn services.agents.src.main:app --reload --port 8000
