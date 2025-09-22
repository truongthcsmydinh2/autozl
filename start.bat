@echo off
echo Starting Tool Auto - Backend and Frontend...
echo.

REM Start both backend and frontend concurrently
npx concurrently --kill-others --prefix-colors "cyan,magenta" --prefix "[{name}]" "python api_server.py" "cd web-dashboard && npm run dev"

echo.
echo Both services stopped.
pause