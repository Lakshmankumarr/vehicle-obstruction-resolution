@echo off
echo ========================================================
echo FreeWay Community Backend - Start Options
echo ========================================================
echo.
echo [1] Local Development (requires Python 3.11+, PostgreSQL, Redis)
echo [2] Docker Development (requires Docker Desktop)
echo [3] Docker Production (requires Docker Desktop + .env config)
echo.
set /p choice="Select option [1-3]: "

if "%choice%"=="1" goto :local
if "%choice%"=="2" goto :dockerdev
if "%choice%"=="3" goto :dockerprod
echo Invalid choice.
pause
goto :eof

:local
echo.
echo Starting local development server...
echo Make sure PostgreSQL and Redis are running!
echo.
cd /d "%~dp0backend"
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt
if not exist .env (
    copy .env.example .env
    echo Created .env from .env.example - please edit with your settings
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