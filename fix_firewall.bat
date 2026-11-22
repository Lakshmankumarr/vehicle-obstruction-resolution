@echo off
echo ========================================================
echo Configuring Windows Firewall for FreeWay Community...
echo (Must be run as Administrator)
echo ========================================================

netsh advfirewall firewall add rule name="FreeWay Expo Metro (8081)" dir=in action=allow protocol=TCP localport=8081
netsh advfirewall firewall add rule name="FreeWay FastAPI (8000)" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall set rule name="Node.js JavaScript Runtime" new enable=no

echo.
echo Setting Wi-Fi network category to Private...
powershell -Command "Get-NetConnectionProfile | Where-Object {.IPv4Connectivity -eq 'Internet'} | Set-NetConnectionProfile -NetworkCategory Private"

echo.
echo Done! Inbound traffic on ports 8081 (Metro) and 8000 (FastAPI) is now allowed.
pause
