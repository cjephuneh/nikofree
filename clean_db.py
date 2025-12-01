#!/usr/bin/env python3
"""
Standalone script to clean the database
Run with: python clean_db.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Flask app
os.environ['FLASK_APP'] = 'app.py'

from app import create_app, db
from app.models import User, Event, Booking, Ticket, Notification, Review

def clean_database():
    """Clean database: delete all events and users except testuser, testpartner, admin"""
    
    app = create_app()
    
    with app.app_context():
        print("="*50)
        print("DATABASE CLEANUP")
        print("="*50)
        print("\nThis will:")
        print("  - Delete ALL events (approved, unapproved, everything)")
        print("  - Delete ALL users EXCEPT: testuser, testpartner, admin")
        print("  - Keep all tables intact")
        print("\n⚠️  WARNING: This action cannot be undone!")
        confirm = input("\nType 'yes' to continue: ").strip().lower()
        
        if confirm != 'yes':
            print("Cancelled.")
            return
        
        try:
            print("\nStarting database cleanup...")
            
            # Step 1: Delete all events
            print("\n1. Deleting all events...")
            events_count = Event.query.count()
            print(f"   Found {events_count} events to delete")
            deleted_events = Event.query.delete()
            print(f"   ✓ Deleted {deleted_events} events")
            
            # Step 2: Find users to keep
            print("\n2. Finding users to keep...")
            users_to_keep = []
            
            # Find testuser
            testuser = User.query.filter(User.email.ilike('%testuser%')).first()
            if testuser:
                users_to_keep.append(testuser.id)
                print(f"   Keeping: {testuser.email} (ID: {testuser.id})")
            
            # Find testpartner
            testpartner = User.query.filter(User.email.ilike('%testpartner%')).first()
            if testpartner and testpartner.id not in users_to_keep:
                users_to_keep.append(testpartner.id)
                print(f"   Keeping: {testpartner.email} (ID: {testpartner.id})")
            
            # Find admin user
            admin_user = User.query.filter(User.email.ilike('%admin%')).first()
            if admin_user and admin_user.id not in users_to_keep:
                users_to_keep.append(admin_user.id)
                print(f"   Keeping: {admin_user.email} (ID: {admin_user.id})")
            
            # Also check config admin email
            from flask import current_app
            admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@nikofree.com')
            config_admin = User.query.filter_by(email=admin_email).first()
            if config_admin and config_admin.id not in users_to_keep:
                users_to_keep.append(config_admin.id)
                print(f"   Keeping (from config): {config_admin.email} (ID: {config_admin.id})")
            
            # Step 3: Delete other users
            print(f"\n3. Deleting users (keeping {len(users_to_keep)} users)...")
            if users_to_keep:
                deleted_users = User.query.filter(~User.id.in_(users_to_keep)).delete(synchronize_session=False)
            else:
                deleted_users = User.query.delete()
            print(f"   ✓ Deleted {deleted_users} users")
            
            # Step 4: Clean orphaned records
            print("\n4. Cleaning orphaned records...")
            orphaned_bookings = Booking.query.filter(~Booking.event_id.in_(db.session.query(Event.id))).delete(synchronize_session=False)
            orphaned_tickets = Ticket.query.filter(~Ticket.booking_id.in_(db.session.query(Booking.id))).delete(synchronize_session=False)
            orphaned_notifications = Notification.query.filter(
                (Notification.event_id.isnot(None)) & 
                (~Notification.event_id.in_(db.session.query(Event.id)))
            ).delete(synchronize_session=False)
            orphaned_reviews = Review.query.filter(
                (Review.event_id.isnot(None)) & 
                (~Review.event_id.in_(db.session.query(Event.id)))
            ).delete(synchronize_session=False)
            
            print(f"   ✓ Deleted {orphaned_bookings} orphaned bookings")
            print(f"   ✓ Deleted {orphaned_tickets} orphaned tickets")
            print(f"   ✓ Deleted {orphaned_notifications} orphaned notifications")
            print(f"   ✓ Deleted {orphaned_reviews} orphaned reviews")
            
            # Commit
            print("\n5. Committing changes...")
            db.session.commit()
            print("   ✓ Changes committed")
            
            # Summary
            print("\n" + "="*50)
            print("CLEANUP SUMMARY")
            print("="*50)
            print(f"Events deleted: {deleted_events}")
            print(f"Users deleted: {deleted_users}")
            print(f"Users kept: {len(users_to_keep)}")
            print(f"Orphaned records cleaned: {orphaned_bookings + orphaned_tickets + orphaned_notifications + orphaned_reviews}")
            print("\n✓ Database cleanup completed!")
            print("="*50)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    clean_database()

