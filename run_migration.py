#!/usr/bin/env python3
"""
Script to add withdrawal_fee column to partner_payouts table
Run this script to fix the database error
"""
import os
import sys
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Get database connection from environment or construct it
def get_db_connection():
    # Try DATABASE_URL first
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        return create_engine(database_url)
    
    # Otherwise construct from individual variables
    db_host = os.getenv('PGHOST', 'localhost')
    db_user = os.getenv('PGUSER', 'postgres')
    db_password = os.getenv('PGPASSWORD', '')
    db_port = os.getenv('PGPORT', '5432')
    db_name = os.getenv('PGDATABASE', 'postgres')
    
    # Construct connection string
    if db_password:
        database_url = f"postgresql://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}"
    else:
        database_url = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
    
    return create_engine(database_url)

def main():
    print("=" * 60)
    print("Adding withdrawal_fee column to partner_payouts table")
    print("=" * 60)
    
    try:
        engine = get_db_connection()
        
        # Test connection
        with engine.connect() as conn:
            print("✓ Connected to database")
            
            # Check if column already exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='partner_payouts' 
                AND column_name='withdrawal_fee'
            """)
            
            result = conn.execute(check_query)
            if result.fetchone():
                print("✓ Column 'withdrawal_fee' already exists")
                return
            
            # Add the column
            print("Adding withdrawal_fee column...")
            alter_query = text("""
                ALTER TABLE partner_payouts 
                ADD COLUMN withdrawal_fee NUMERIC(10, 2) DEFAULT 0.00
            """)
            
            conn.execute(alter_query)
            conn.commit()
            
            print("✓ Column 'withdrawal_fee' added successfully")
            
            # Update existing records
            print("Updating existing records...")
            update_query = text("""
                UPDATE partner_payouts 
                SET withdrawal_fee = 0.00 
                WHERE withdrawal_fee IS NULL
            """)
            
            result = conn.execute(update_query)
            conn.commit()
            
            print(f"✓ Updated {result.rowcount} existing records")
            print("\n" + "=" * 60)
            print("Migration completed successfully!")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease check your database connection settings:")
        print("- DATABASE_URL environment variable, or")
        print("- PGHOST, PGUSER, PGPASSWORD, PGPORT, PGDATABASE variables")
        sys.exit(1)

if __name__ == '__main__':
    main()

