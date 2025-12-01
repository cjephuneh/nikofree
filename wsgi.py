"""
WSGI entry point for gunicorn
This file creates the Flask app instance that gunicorn will use
"""
import os
from app import create_app

# Create the Flask app instance
# Use 'production' config for Azure deployment, or get from environment
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

