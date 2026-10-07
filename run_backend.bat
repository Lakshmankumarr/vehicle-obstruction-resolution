@echo off
echo ========================================================
echo Starting FreeWay Community Backend (FastAPI + Uvicorn)...
echo ========================================================
cd /d "%~dp0backend"
set PYTHONPATH=%cd%
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
