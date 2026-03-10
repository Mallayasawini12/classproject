@echo off
REM Quick Deploy Script - Runs EmotiSense with Ngrok for public access
echo ================================================
echo   EmotiSense - Quick Public Deployment
echo ================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please create it first: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Set environment variables
set FLASK_HOST=127.0.0.1
set FLASK_PORT=5000
set FLASK_DEBUG=false
set FLASK_ENV=production

echo Starting EmotiSense server...
echo.

REM Start the Flask app in background
start /B python app.py

REM Wait for server to start
timeout /t 5 /nobreak > nul

echo.
echo ================================================
echo Server is running at http://127.0.0.1:5000
echo ================================================
echo.
echo To make it PUBLIC, you have 3 options:
echo.
echo 1. NGROK (Recommended for quick demo):
echo    - Download from: https://ngrok.com/download
echo    - Run: ngrok http 5000
echo    - Share the URL it gives you (e.g., https://abc123.ngrok.io)
echo.
echo 2. RAILWAY (Recommended for production):
echo    - See VERCEL_DEPLOYMENT.md for instructions
echo.
echo 3. RENDER (Free tier available):
echo    - See VERCEL_DEPLOYMENT.md for instructions
echo.
echo ================================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Keep the window open
cmd /k
