@echo off
echo ====================================================
echo Starting DesiFinds Development Servers...
echo ====================================================

echo.
echo 1. Starting FastAPI Backend Server on port 8080...
start "DesiFinds Backend" cmd /k "cd backend && .venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload"

echo 2. Starting React Frontend Server on port 19993...
set PORT=19993
set BASE_PATH=/
start "DesiFinds Frontend" cmd /k "cd frontend && pnpm run dev"

echo.
echo Backend URL: http://localhost:8080
echo Frontend URL: http://localhost:19993
echo ====================================================
pause
