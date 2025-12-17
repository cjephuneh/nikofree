#!/usr/bin/env python3
"""
Flask-based migration script to add withdrawal_fee column to partner_payouts table
This uses the Flask app context so all dependencies are available
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def main():
    print("=" * 60)
    print("Adding withdrawal_fee column to partner_payouts table")
    print("=" * 60)
    
    # Create Flask app context
    app = create_app('default')
    
    with app.app_context():
        try:
            # Check if column already exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='partner_payouts' 
                AND column_name='withdrawal_fee'
            """)
            
            result = db.session.execute(check_query)
            if result.fetchone():
                print("✓ Column 'withdrawal_fee' already exists")
                return
            
            # Add the column
            print("Adding withdrawal_fee column...")
            alter_query = text("""
                ALTER TABLE partner_payouts 
                ADD COLUMN withdrawal_fee NUMERIC(10, 2) DEFAULT 0.00
            """)
            
            db.session.execute(alter_query)
            db.session.commit()
            
            print("✓ Column 'withdrawal_fee' added successfully")
            
            # Update existing records
            print("Updating existing records...")
            update_query = text("""
                UPDATE partner_payouts 
                SET withdrawal_fee = 0.00 
                WHERE withdrawal_fee IS NULL
            """)
            
            result = db.session.execute(update_query)
            db.session.commit()
            
            print(f"✓ Updated {result.rowcount} existing records")
            print("\n" + "=" * 60)
            print("Migration completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    main()

