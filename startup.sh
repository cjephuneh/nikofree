#!/bin/bash
# Azure App Service startup script
# This ensures gunicorn uses the correct WSGI entry point

gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app

