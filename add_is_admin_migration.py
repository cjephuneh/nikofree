#!/usr/bin/env python3
"""
Migration script to add is_admin column to users table
Run this script to add the is_admin field to existing users table
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def add_is_admin_column():
    """Add is_admin column to users table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='is_admin'
            """))
            
            if result.fetchone():
                print("✅ Column 'is_admin' already exists in users table")
                return
            
            # Add the column
            print("Adding is_admin column to users table...")
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN is_admin BOOLEAN DEFAULT FALSE
            """))
            
            # Create index for better query performance
            print("Creating index on is_admin column...")
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_is_admin ON users(is_admin)
            """))
            
            # Set existing admin users (if ADMIN_EMAIL is configured)
            admin_email = app.config.get('ADMIN_EMAIL')
            if admin_email:
                print(f"Setting is_admin=True for user with email: {admin_email}")
                db.session.execute(text("""
                    UPDATE users 
                    SET is_admin = TRUE 
                    WHERE LOWER(email) = LOWER(:email)
                """), {'email': admin_email})
            
            db.session.commit()
            print("✅ Successfully added is_admin column to users table")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding is_admin column: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    add_is_admin_column()

