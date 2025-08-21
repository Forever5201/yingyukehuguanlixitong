@echo off
cd /d "%~dp0"

echo ========================================
echo     Customer Management System - Start
echo ========================================
echo.

echo [%time%] Starting system...
echo.
echo System Info:
echo     - URL: http://localhost:5000
echo     - Press Ctrl+C to stop server
echo     - Database: instance/database.sqlite
echo.
echo ========================================
echo.

REM Start browser after 3 seconds
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

REM Start Flask application
python run.py

echo.
echo [%time%] Server stopped
pause