#!/bin/bash
# Azure App Service startup script
# This ensures gunicorn uses the correct WSGI entry point

# Set working directory to deployment root
cd /home/site/wwwroot || exit 1

# Add current directory to Python path
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

# Use PORT from environment if set, otherwise default to 8000
PORT=${PORT:-8000}

# Verify files exist
if [ ! -f "wsgi.py" ] && [ ! -f "app.py" ]; then
    echo "ERROR: Neither wsgi.py nor app.py found in /home/site/wwwroot"
    echo "Current directory: $(pwd)"
    echo "Files in directory:"
    ls -la
    exit 1
fi

# Try wsgi.py first, fallback to app.py
if [ -f "wsgi.py" ]; then
    echo "Starting gunicorn with wsgi.py..."
    exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
elif [ -f "app.py" ]; then
    echo "Starting gunicorn with app.py..."
    exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile - app:app
else
    echo "ERROR: No valid entry point found"
    exit 1
fi

