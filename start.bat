@echo off
echo 🎃 Starting Halloween Quest Bot + API Server...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment  
call venv\Scripts\activate.bat

REM Install requirements if needed
if not exist "venv\.installed" (
    echo Installing requirements...
    pip install -r requirements.txt
    echo. > venv\.installed
)

REM Create uploads directory
if not exist "uploads\photos" mkdir uploads\photos

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file...
    (
    echo BOT_TOKEN=7909656312:AAEtxP0EFV4PqmttfhHMTdCZz_pRIH9_H2I
    echo BOT_USERNAME=imashaquestbot
    echo API_HOST=0.0.0.0
    echo API_PORT=8080
    echo WEB_APP_URL=https://imasha.ru
    echo PHOTOS_DIR=./uploads/photos
    ) > .env
)

REM Start the application
echo Starting bot and API server...
echo Bot: @imashaquestbot
echo API: http://localhost:8080
echo.
echo Press Ctrl+C to stop
echo.

python main.py

pause
