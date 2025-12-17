#!/usr/bin/env python3
"""
Migration script to add reserved_until column to bookings table
Run this script to add the reserved_until field for 5-minute ticket reservation timer
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def add_reserved_until_column():
    """Add reserved_until column to bookings table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='bookings' AND column_name='reserved_until'
            """))
            
            if result.fetchone():
                print("✅ Column 'reserved_until' already exists in bookings table")
                return
            
            # Add the column
            print("Adding reserved_until column to bookings table...")
            db.session.execute(text("""
                ALTER TABLE bookings 
                ADD COLUMN reserved_until TIMESTAMP
            """))
            
            # Create index for better query performance
            print("Creating index on reserved_until column...")
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_bookings_reserved_until ON bookings(reserved_until)
            """))
            
            db.session.commit()
            print("✅ Successfully added reserved_until column to bookings table")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding reserved_until column: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    add_reserved_until_column()

