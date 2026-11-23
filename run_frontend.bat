@echo off
setlocal
echo ========================================================
echo FreeWay Community Mobile App - Fast Launcher
echo ========================================================
echo.
echo [1] Expo LAN Mode (Press Enter - Instant Start for Phone)
echo [2] Expo LAN Mode with Cache Clear
echo [3] Expo Localhost Only
echo [4] Android Build (requires Android Studio)
echo.
set "choice=1"
set /p choice="Select option [1-4] (Default: 1): "

if "%choice%"=="1" goto :fast_lan
if "%choice%"=="2" goto :reset
if "%choice%"=="3" goto :local
if "%choice%"=="4" goto :android
goto :fast_lan

:fast_lan
echo.
echo Starting Expo with LAN access instantly...
cd /d "%~dp0FreewayApp"
npx expo start --lan
pause
goto :eof

:reset
echo.
echo Starting Expo with cache reset...
cd /d "%~dp0FreewayApp"
npx expo start --lan -c
pause
goto :eof

:local
echo.
echo Starting Expo (localhost only)...
cd /d "%~dp0FreewayApp"
npx expo start
pause
goto :eof

:android
echo.
echo Building for Android...
cd /d "%~dp0FreewayApp"
npx expo run:android
pause
goto :eof
