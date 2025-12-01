#!/usr/bin/env python3
"""
Script to clean the database:
- Delete all events (and related data)
- Delete all users except: testpartner, testuser, and admin
- Keep all tables intact
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Partner, Event, Booking, Ticket, TicketType, PromoCode, EventPromotion, EventHost, EventInterest, Notification, Review, Payment

# Users to keep
USERS_TO_KEEP = ['testuser', 'testpartner', 'admin']

def clean_database():
    """Clean the database as specified"""
    app = create_app()
    
    with app.app_context():
        print("Starting database cleanup...")
        
        # Step 1: Delete all events (this will cascade delete related records)
        print("\n1. Deleting all events...")
        events_count = Event.query.count()
        print(f"   Found {events_count} events to delete")
        
        # Delete events (cascade will handle related records)
        deleted_events = Event.query.delete()
        print(f"   Deleted {deleted_events} events")
        
        # Step 2: Delete all users except the ones to keep
        print("\n2. Deleting users (keeping testuser, testpartner, admin)...")
        
        # Find users to keep - search by email containing the username (case insensitive)
        users_to_keep = []
        
        # Find testuser
        testuser = User.query.filter(User.email.ilike('%testuser%')).first()
        if testuser:
            users_to_keep.append(testuser.id)
            print(f"   Keeping user: {testuser.email} (ID: {testuser.id})")
        
        # Find testpartner (might be a Partner, not a User - check both)
        testpartner_user = User.query.filter(User.email.ilike('%testpartner%')).first()
        if testpartner_user:
            users_to_keep.append(testpartner_user.id)
            print(f"   Keeping user: {testpartner_user.email} (ID: {testpartner_user.id})")
        
        # Find admin user (check common admin email patterns)
        admin_user = User.query.filter(
            (User.email.ilike('%admin%')) | 
            (User.email == 'admin@nikofree.com') |
            (User.email == 'admin@test.com')
        ).first()
        if admin_user and admin_user.id not in users_to_keep:
            users_to_keep.append(admin_user.id)
            print(f"   Keeping admin user: {admin_user.email} (ID: {admin_user.id})")
        
        # Also check config for admin email
        from flask import current_app
        admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@nikofree.com')
        config_admin = User.query.filter_by(email=admin_email).first()
        if config_admin and config_admin.id not in users_to_keep:
            users_to_keep.append(config_admin.id)
            print(f"   Keeping admin from config: {config_admin.email} (ID: {config_admin.id})")
        
        # Delete all other users
        if users_to_keep:
            deleted_users = User.query.filter(~User.id.in_(users_to_keep)).delete(synchronize_session=False)
        else:
            deleted_users = User.query.delete()
        
        print(f"   Deleted {deleted_users} users")
        print(f"   Kept {len(users_to_keep)} users")
        
        # Step 3: Clean up any orphaned records
        print("\n3. Cleaning up orphaned records...")
        
        # Delete orphaned bookings (should be handled by cascade, but just in case)
        orphaned_bookings = Booking.query.filter(~Booking.event_id.in_(
            db.session.query(Event.id)
        )).delete(synchronize_session=False)
        print(f"   Deleted {orphaned_bookings} orphaned bookings")
        
        # Delete orphaned tickets
        orphaned_tickets = Ticket.query.filter(~Ticket.booking_id.in_(
            db.session.query(Booking.id)
        )).delete(synchronize_session=False)
        print(f"   Deleted {orphaned_tickets} orphaned tickets")
        
        # Delete orphaned notifications related to deleted events/users
        orphaned_notifications = Notification.query.filter(
            (Notification.event_id.isnot(None)) & 
            (~Notification.event_id.in_(db.session.query(Event.id)))
        ).delete(synchronize_session=False)
        print(f"   Deleted {orphaned_notifications} orphaned notifications")
        
        # Delete orphaned reviews
        orphaned_reviews = Review.query.filter(
            (Review.event_id.isnot(None)) & 
            (~Review.event_id.in_(db.session.query(Event.id)))
        ).delete(synchronize_session=False)
        print(f"   Deleted {orphaned_reviews} orphaned reviews")
        
        # Commit all changes
        print("\n4. Committing changes...")
        db.session.commit()
        print("   ✓ Changes committed successfully")
        
        # Print summary
        print("\n" + "="*50)
        print("CLEANUP SUMMARY")
        print("="*50)
        print(f"Events deleted: {deleted_events}")
        print(f"Users deleted: {deleted_users}")
        print(f"Users kept: {len(users_to_keep)}")
        print(f"Orphaned bookings deleted: {orphaned_bookings}")
        print(f"Orphaned tickets deleted: {orphaned_tickets}")
        print(f"Orphaned notifications deleted: {orphaned_notifications}")
        print(f"Orphaned reviews deleted: {orphaned_reviews}")
        print("\n✓ Database cleanup completed successfully!")
        print("="*50)

if __name__ == '__main__':
    # Confirm before proceeding
    print("="*50)
    print("DATABASE CLEANUP SCRIPT")
    print("="*50)
    print("\nThis script will:")
    print("  - Delete ALL events (approved, unapproved, everything)")
    print("  - Delete ALL users EXCEPT: testuser, testpartner, admin")
    print("  - Keep all tables intact")
    print("\n⚠️  WARNING: This action cannot be undone!")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    
    try:
        clean_database()
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        sys.exit(1)

