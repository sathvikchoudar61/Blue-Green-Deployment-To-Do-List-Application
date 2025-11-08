@echo off
echo Starting Blue-Green Deployment Test...
echo.
echo Starting Blue server on port 5001...
start cmd /k "set SERVER_NAME=Blue&& set SERVER_PORT=5001&& set SERVER_COLOR=blue&& python app.py"
timeout /t 3 /nobreak > nul
echo.
echo Starting Green server on port 5002...
start cmd /k "set SERVER_NAME=Green&& set SERVER_PORT=5002&& set SERVER_COLOR=green&& python app.py"
timeout /t 3 /nobreak > nul
echo.
echo Starting router on port 5000...
start "Router" cmd /c "python router.py > router.log 2>&1"
echo.
echo Servers starting...
echo Blue server: http://localhost:5001
echo Green server: http://localhost:5002
echo Router: http://localhost:5000
echo.
echo Press any key to stop all servers...
pause > nul
echo Stopping servers...
taskkill /F /IM python.exe > nul 2>&1
echo Done!