#!/bin/bash
# Production startup script for EmotiSense

echo "Starting EmotiSense in production mode..."

# Set environment variables
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export FLASK_DEBUG=false
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found!"
    echo "Please create it with: python -m venv .venv"
    exit 1
fi

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn
fi

# Run with gunicorn
echo "Starting server on $FLASK_HOST:$FLASK_PORT"
gunicorn --config gunicorn_config.py wsgi:app
