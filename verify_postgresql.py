#!/usr/bin/env python3
"""
Quick verification script to check PostgreSQL connection and data
"""

import os
import sys
from app import create_app, db
from app.models import User, Event, Partner, Booking, Ticket, Category, Location

def main():
    """Verify PostgreSQL connection and data"""
    print("="*60)
    print("PostgreSQL Verification")
    print("="*60)
    
    app = create_app('default')
    
    with app.app_context():
        # Check database URI
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        print(f"\nDatabase URI: {db_uri[:50]}..." if len(db_uri) > 50 else f"\nDatabase URI: {db_uri}")
        
        # Check if using PostgreSQL
        if 'postgresql' in db_uri.lower():
            print("✓ Using PostgreSQL")
        elif 'sqlite' in db_uri.lower():
            print("⚠ Using SQLite (PostgreSQL not configured)")
        else:
            print("? Unknown database type")
        
        try:
            # Test connection
            db.engine.connect()
            print("✓ Database connection successful")
            
            # Count records
            print("\n" + "="*60)
            print("Data Verification")
            print("="*60)
            
            users_count = User.query.count()
            events_count = Event.query.count()
            partners_count = Partner.query.count()
            bookings_count = Booking.query.count()
            tickets_count = Ticket.query.count()
            categories_count = Category.query.count()
            locations_count = Location.query.count()
            
            print(f"\nUsers: {users_count}")
            print(f"Partners: {partners_count}")
            print(f"Events: {events_count}")
            print(f"Bookings: {bookings_count}")
            print(f"Tickets: {tickets_count}")
            print(f"Categories: {categories_count}")
            print(f"Locations: {locations_count}")
            
            if users_count > 0 or events_count > 0:
                print("\n✓ Data migration verified - records found in database")
            else:
                print("\n⚠ No data found - migration may not have completed")
            
            print("\n" + "="*60)
            print("Verification Complete!")
            print("="*60)
            
        except Exception as e:
            print(f"\n✗ Database connection failed: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()

