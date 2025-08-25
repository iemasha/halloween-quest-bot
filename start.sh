#!/bin/bash

# Halloween Quest Telegram Bot Launcher
echo "🎃 Starting Halloween Quest Bot + API Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Create uploads directory
mkdir -p uploads/photos

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
BOT_TOKEN=7909656312:AAEtxP0EFV4PqmttfhHMTdCZz_pRIH9_H2I
BOT_USERNAME=imashaquestbot
API_HOST=0.0.0.0
API_PORT=8080
WEB_APP_URL=https://imasha.ru
PHOTOS_DIR=./uploads/photos
EOF
fi

# Start the application
echo "Starting bot and API server..."
echo "Bot: @imashaquestbot"
echo "API: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python main.py
