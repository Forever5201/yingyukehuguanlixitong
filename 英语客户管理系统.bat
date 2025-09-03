@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo     Customer Management System - Start
echo ========================================
echo.

echo [%time%] Starting system...
echo.

REM Check virtual environment
if exist "venv\Scripts\activate.bat" (
    echo [%time%] Activating virtual environment...
    call venv\Scripts\activate.bat
    echo [%time%] Virtual environment activated
) else (
    echo [%time%] WARNING: Virtual environment not found
    echo       Recommendation: python -m venv venv
)

echo.

REM Check Python environment
echo [%time%] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found, please install Python 3.x first
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [%time%] Python environment check passed

REM Quick check core dependencies
echo [%time%] Checking core dependencies...
pip show Flask >nul 2>&1
if %errorlevel% neq 0 (
    echo [%time%] Installing Flask dependencies...
    pip install Flask Flask-SQLAlchemy Flask-Migrate
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo [%time%] Dependencies installed successfully
) else (
    echo [%time%] Core dependencies check passed
)

REM Check database
echo [%time%] Checking database status...
if not exist "instance\database.sqlite" (
    echo [%time%] Database not found, initializing...
    python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [%time%] Database initialized successfully
    ) else (
        echo [%time%] WARNING: Database initialization may have issues
    )
) else (
    echo [%time%] Database file exists
)

echo.
echo System Info:
echo     - URL: http://localhost:5000
echo     - Press Ctrl+C to stop server
echo     - Database: instance/database.sqlite
if exist "venv\Scripts\activate.bat" (
    echo     - Environment: Virtual Environment (venv)
) else (
    echo     - Environment: System Python
)
echo.
echo ========================================
echo.

REM Start browser after 3 seconds
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

REM Start Flask application
echo [%time%] Starting Flask application...
python run.py

echo.
echo [%time%] Server stopped
pause