@echo off
title AI Grievance System Launcher
echo ===================================================
echo   Starting AI Grievance & Intelligent Routing Portal
echo ===================================================
echo.

:: 1. Launch FastAPI Backend in a minimized terminal window
echo [1/2] Launching Backend API Server (FastAPI)...
start "FastAPI Backend" /min cmd /k "cd /d %~dp0backend && uvicorn main:app --reload"

:: Wait 3 seconds to ensure backend is initialized first
timeout /t 3 /nobreak >nul

:: 2. Launch Streamlit Frontend (Automatically opens your browser)
echo [2/2] Launching Frontend Portal (Streamlit)...
start "Streamlit Frontend" /min cmd /k "cd /d %~dp0frontend && streamlit run app.py"

echo.
echo ===================================================
echo   Portal is running! Opening in your browser...
echo ===================================================
exit