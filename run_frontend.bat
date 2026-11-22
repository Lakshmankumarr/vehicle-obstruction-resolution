@echo off
echo ========================================================
echo FreeWay Community Mobile App - Start Options
echo ========================================================
echo.
echo [1] Expo Development Server (LAN - for physical device testing)
echo [2] Expo Development Server (localhost only)
echo [3] Expo Development Server (with cache reset)
echo [4] Android Build (requires Android Studio)
echo [5] iOS Build (requires macOS + Xcode)
echo [6] Production Build - Android AAB
echo [7] Production Build - iOS IPA (macOS only)
echo.
set /p choice="Select option [1-7]: "

if "%choice%"=="1" goto :lan
if "%choice%"=="2" goto :local
if "%choice%"=="3" goto :reset
if "%choice%"=="4" goto :android
if "%choice%"=="5" goto :ios
if "%choice%"=="6" goto :aab
if "%choice%"=="7" goto :ipa
echo Invalid choice.
pause
goto :eof

:lan
echo.
echo Starting Expo with LAN access...
echo Make sure your phone is on the same Wi-Fi network!
echo.
cd /d "%~dp0FreewayApp"
if not exist node_modules (
    echo Installing dependencies...
    npm install
)
npx expo start --lan
pause
goto :eof

:local
echo.
echo Starting Expo (localhost only)...
echo.
cd /d "%~dp0FreewayApp"
if not exist node_modules npm install
npx expo start
pause
goto :eof

:reset
echo.
echo Starting Expo with cache reset...
echo.
cd /d "%~dp0FreewayApp"
if not exist node_modules npm install
npx expo start --clear
pause
goto :eof

:android
echo.
echo Building for Android...
echo.
cd /d "%~dp0FreewayApp"
if not exist node_modules npm install
npx expo run:android
pause
goto :eof

:ios
echo.
echo Building for iOS (macOS only)...
echo.
cd /d "%~dp0FreewayApp"
if not exist node_modules npm install
npx expo run:ios
pause
goto :eof

:aab
echo.
echo Building production Android App Bundle (AAB)...
echo Requires EAS CLI: npm install -g eas-cli
echo.
cd /d "%~dp0FreewayApp"
if not exist node_modules npm install
eas build --platform android --profile production
pause
goto :eof

:ipa
echo.
echo Building production iOS App (IPA)...
echo Requires macOS + Xcode + EAS CLI
echo.
cd /d "%~dp0FreewayApp"
if not exist node_modules npm install
eas build --platform ios --profile production
pause
goto :eof