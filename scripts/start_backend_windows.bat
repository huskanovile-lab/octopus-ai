@echo off
setlocal

REM Windows CMD/PowerShell backend startup
REM Prefer Python 3.12 to avoid pydantic-core build failures on newer interpreters.
where py >nul 2>nul
if %errorlevel%==0 (
  py -3.12 --version >nul 2>nul
  if %errorlevel%==0 (
    set "PYEXE=py -3.12"
  ) else (
    echo [ERROR] Python 3.12 not found. Install Python 3.12 from python.org and retry.
    echo [TIP] During install, enable "Add Python to PATH" and install for current user.
    exit /b 1
  )
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    for /f "tokens=2" %%v in ('python -V 2^>^&1') do set PYVER=%%v
    echo [WARN] using system python %PYVER% (recommended: Python 3.12)
    set "PYEXE=python"
  ) else (
    echo [ERROR] Python launcher not found.
    exit /b 1
  )
)

if not exist .venv (
  %PYEXE% -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
pip install -r services\agents\requirements.txt
if %errorlevel% neq 0 (
  echo [ERROR] dependency install failed. Ensure Python 3.12 is used.
  exit /b 1
)

python scripts\run_demo_session.py
python -m uvicorn services.agents.src.main:app --reload --port 8000

endlocal
