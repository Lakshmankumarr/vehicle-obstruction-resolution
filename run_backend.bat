@echo off
setlocal
echo ========================================================
echo FreeWay Community Backend - Fast Launcher
echo ========================================================
echo.
echo [1] Fast Local Development (Press Enter - Instant Start)
echo [2] Install/Update Dependencies + Start
echo [3] Docker Development
echo [4] Docker Production
echo.
set "choice=1"
set /p choice="Select option [1-4] (Default: 1): "

if "%choice%"=="1" goto :fast_local
if "%choice%"=="2" goto :install_local
if "%choice%"=="3" goto :dockerdev
if "%choice%"=="4" goto :dockerprod
goto :fast_local

:fast_local
echo.
echo Starting FastAPI Backend instantly...
cd /d "%~dp0backend"
set PYTHONPATH=%cd%
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
goto :eof

:install_local
echo.
echo Checking/Installing dependencies...
cd /d "%~dp0backend"
set PYTHONPATH=%cd%
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)
pip install -r requirements.txt
if not exist .env (
    copy .env.example .env
    echo Created .env from .env.example
)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
goto :eof

:dockerdev
echo.
echo Starting Docker development environment...
echo.
cd /d "%~dp0"
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
pause
goto :eof

:dockerprod
echo.
echo Starting Docker production environment...
echo Make sure .env file is configured!
echo.
cd /d "%~dp0"
if not exist .env (
    copy .env.production .env
    echo Created .env from .env.production - PLEASE EDIT WITH YOUR SECRETS!
    pause
)
docker-compose up --build -d
echo.
echo Services started in background.
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo To view logs: docker-compose logs -f backend
echo To stop: docker-compose down
pause
goto :eof
