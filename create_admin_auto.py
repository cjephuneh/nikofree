#!/usr/bin/env python3
"""
Automatically create admin user with default credentials
"""
import sys
import os

# Activate venv if it exists
venv_path = os.path.join(os.path.dirname(__file__), 'venv')
if os.path.exists(venv_path):
    # Add venv to path
    sys.path.insert(0, os.path.join(venv_path, 'lib', 'python3.13', 'site-packages'))
    sys.path.insert(0, os.path.join(venv_path, 'lib', 'python3.12', 'site-packages'))
    sys.path.insert(0, os.path.join(venv_path, 'lib', 'python3.11', 'site-packages'))
    sys.path.insert(0, os.path.join(venv_path, 'lib', 'python3.10', 'site-packages'))

from app import create_app, db
from app.models.user import User

def create_admin():
    app = create_app()
    
    with app.app_context():
        admin_email = 'admin@nikofree.com'
        admin_password = 'Admin@1234'
        
        print("Creating admin user...")
        
        # Check if user exists
        user = User.query.filter_by(email=admin_email).first()
        if user:
            # User exists, update password
            user.set_password(admin_password)
            user.is_active = True
            user.is_verified = True
            user.email_verified = True
            db.session.commit()
            print(f"✓ User {admin_email} already exists. Password reset to: {admin_password}")
        else:
            # Create new admin user
            admin = User(
                email=admin_email,
                first_name='System',
                last_name='Administrator',
                oauth_provider='email',
                is_verified=True,
                email_verified=True,
                is_active=True
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Admin user created successfully!")
        
        print(f"\nAdmin Credentials:")
        print(f"  Email: {admin_email}")
        print(f"  Password: {admin_password}")
        print(f"\nYou can now login to the admin dashboard!")

if __name__ == '__main__':
    create_admin()

