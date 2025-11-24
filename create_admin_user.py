#!/usr/bin/env python3
"""
Script to create an admin user for the root app
Usage: python create_admin_user.py
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User

def create_admin_user():
    """Create an admin user"""
    app = create_app()
    
    with app.app_context():
        # Default admin credentials
        admin_email = 'admin@nikofree.com'
        admin_password = 'Admin@1234'
        admin_first_name = 'System'
        admin_last_name = 'Administrator'
        
        print("=" * 60)
        print("Niko Free - Admin User Creation")
        print("=" * 60)
        print()
        
        # Check if admin already exists
        existing_user = User.query.filter_by(email=admin_email).first()
        if existing_user:
            print(f"✓ User with email {admin_email} already exists.")
            print(f"\nTo use this user as admin, make sure:")
            print(f"  1. ADMIN_EMAIL in config.py is set to: {admin_email}")
            print(f"  2. The password is correct")
            print(f"\nTo reset the password, you can update it manually in the database.")
            return
        
        # Create admin user
        admin_user = User(
            email=admin_email,
            first_name=admin_first_name,
            last_name=admin_last_name,
            is_active=True,
            is_verified=True,
            email_verified=True,
            oauth_provider='email'
        )
        admin_user.set_password(admin_password)
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✓ Admin user created successfully!")
            print("=" * 60)
            print(f"\n⚠️  ADMIN CREDENTIALS:")
            print(f"  Email: {admin_email}")
            print(f"  Password: {admin_password}")
            print(f"\n⚠️  IMPORTANT:")
            print(f"  1. Make sure ADMIN_EMAIL in config.py is set to: {admin_email}")
            print(f"  2. Change the password after first login!")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error creating admin user: {str(e)}")
            import traceback
            traceback.print_exc()
            return

if __name__ == '__main__':
    create_admin_user()

