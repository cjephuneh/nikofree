"""
WSGI entry point for gunicorn
This file creates the Flask app instance that gunicorn will use
"""
import os
from app import create_app, db
from flask_migrate import upgrade as migrate_upgrade

# Create the Flask app instance
# Use 'production' config for Azure deployment, or get from environment
app = create_app(os.getenv('FLASK_ENV', 'production'))

# Run database migrations on startup in production
# This ensures the database is up-to-date when the app starts
if os.getenv('FLASK_ENV') == 'production' or os.getenv('RUN_MIGRATIONS_ON_STARTUP', '').lower() == 'true':
    with app.app_context():
        try:
            print("Running database migrations...")
            migrate_upgrade()
            print("Database migrations completed successfully.")
        except Exception as e:
            print(f"Warning: Database migration failed: {e}")
            print("The application will continue to start, but some features may not work correctly.")
            print("Please run 'flask db upgrade' manually to fix this issue.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

