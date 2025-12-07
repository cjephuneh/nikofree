#!/bin/bash
# Azure App Service startup script
# This ensures gunicorn uses the correct WSGI entry point

# Use PORT from environment if set, otherwise default to 8000
PORT=${PORT:-8000}

# Start gunicorn
gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app

