@echo off
echo ==========================================================
echo DataPilot: Natural Language to SQL Analytics Agent Setup
echo ==========================================================
cd /d "%~dp0"

echo [1/3] Seeding E-Commerce Sample Database...
call backend\venv\Scripts\python.exe database\seed.py

echo [2/3] Starting Backend Server in new window...
start "DataPilot Backend" cmd /c "start_backend.bat"

echo [3/3] Starting Frontend Server in new window...
start "DataPilot Frontend" cmd /c "start_frontend.bat"

echo ==========================================================
echo Services launched!
echo - Frontend: http://localhost:5173
echo - Backend:  http://localhost:8000
echo - Swagger:  http://localhost:8000/docs
echo ==========================================================
