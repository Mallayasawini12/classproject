@echo off
REM Production startup script for EmotiSense (Windows)

echo Starting EmotiSense in production mode...

REM Set environment variables
set FLASK_HOST=0.0.0.0
set FLASK_PORT=5000
set FLASK_DEBUG=false
set FLASK_ENV=production
set PYTHONUNBUFFERED=1

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found!
    echo Please create it with: python -m venv .venv
    exit /b 1
)

REM Check if gunicorn is installed
pip show gunicorn >nul 2>&1
if errorlevel 1 (
    echo Installing gunicorn...
    pip install gunicorn
)

REM Run with gunicorn
echo Starting server on %FLASK_HOST%:%FLASK_PORT%
gunicorn --config gunicorn_config.py wsgi:app
