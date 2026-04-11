@echo off
setlocal

REM Run from repo root on Windows CMD
if not exist .venv (
  py -3 -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r services\agents\requirements.txt
python scripts\run_demo_session.py
python -m uvicorn services.agents.src.main:app --reload --port 8000

endlocal
