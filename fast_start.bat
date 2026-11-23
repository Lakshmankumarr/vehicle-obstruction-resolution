@echo off
title FreeWay Community - 1-Click Fast Launcher
echo ========================================================
echo   FreeWay Community - Starting Backend + Expo Frontend
echo ========================================================
echo.

echo [1/2] Starting FastAPI Backend on port 8000...
start "FreeWay Backend (Port 8000)" cmd /k "cd /d %~dp0backend && set PYTHONPATH=%cd% && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting Expo Metro Bundler on port 8081 (LAN)...
start "FreeWay Metro Bundler (Port 8081)" cmd /k "cd /d %~dp0FreewayApp && npx expo start --lan"

echo.
echo ========================================================
echo   Both services started in dedicated terminal windows!
echo   - Backend API: http://192.168.29.87:8000
echo   - Expo Metro:  exp://192.168.29.87:8081
echo ========================================================
echo.
echo You can keep this window open or close it.
timeout /t 5
