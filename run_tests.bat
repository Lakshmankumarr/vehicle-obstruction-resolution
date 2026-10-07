@echo off
echo ========================================================
echo Running FreeWay Community Backend Test Suite (Pytest)...
echo ========================================================
cd /d "%~dp0backend"
set PYTHONPATH=%cd%
python -m pytest tests/ -v --cov=app
pause
