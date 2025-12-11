#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to PostgreSQL

Usage:
    python migrate_to_postgresql.py

This script will:
1. Connect to the SQLite database
2. Connect to PostgreSQL database
3. Transfer all data while preserving relationships
4. Handle foreign keys and relationships properly
"""

import os
import sys
from urllib.parse import quote_plus
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import traceback

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import (
    User, Partner, Event, EventHost, EventInterest, EventPromotion,
    Ticket, TicketType, Booking, PromoCode, Payment, PartnerPayout,
    Category, Location, Notification, AdminLog, Review
)
from app import db

# Models in order of dependency (parents before children)
MODEL_ORDER = [
    Category,
    Location,
    User,
    Partner,
    Event,
    EventHost,
    EventInterest,
    EventPromotion,
    TicketType,
    Booking,
    Ticket,
    PromoCode,
    Payment,
    PartnerPayout,
    Notification,
    AdminLog,
    Review,
]


def get_table_name(model):
    """Get the table name for a model"""
    return model.__tablename__


def migrate_table(session_sqlite, session_postgres, model_class, model_name):
    """Migrate a single table from SQLite to PostgreSQL"""
    print(f"\n{'='*60}")
    print(f"Migrating {model_name}...")
    print(f"{'='*60}")
    
    try:
        # Get all records from SQLite
        records = session_sqlite.query(model_class).all()
        total = len(records)
        
        if total == 0:
            print(f"  No {model_name} records to migrate.")
            return 0
        
        print(f"  Found {total} {model_name} records")
        
        # Check if table exists in PostgreSQL
        inspector = inspect(session_postgres.bind)
        table_name = get_table_name(model_class)
        
        if not inspector.has_table(table_name):
            print(f"  Warning: Table {table_name} does not exist in PostgreSQL. Skipping.")
            return 0
        
        # Get existing records in PostgreSQL to avoid duplicates
        existing_ids = set()
        try:
            existing = session_postgres.query(model_class).all()
            existing_ids = {r.id for r in existing}
            print(f"  Found {len(existing_ids)} existing records in PostgreSQL")
        except Exception as e:
            print(f"  Could not check existing records: {e}")
        
        migrated = 0
        skipped = 0
        errors = 0
        
        for record in records:
            try:
                # Skip if already exists
                if record.id in existing_ids:
                    skipped += 1
                    continue
                
                # Convert SQLite record to dict
                record_dict = {}
                for column in model_class.__table__.columns:
                    value = getattr(record, column.name)
                    # Handle datetime objects
                    if isinstance(value, datetime):
                        record_dict[column.name] = value
                    else:
                        record_dict[column.name] = value
                
                # Create new record in PostgreSQL
                new_record = model_class(**record_dict)
                session_postgres.add(new_record)
                
                migrated += 1
                
                # Commit in batches of 100
                if migrated % 100 == 0:
                    session_postgres.commit()
                    print(f"  Migrated {migrated}/{total} records...")
                
            except IntegrityError as e:
                session_postgres.rollback()
                errors += 1
                print(f"  Error migrating {model_name} ID {record.id}: {e}")
                continue
            except Exception as e:
                session_postgres.rollback()
                errors += 1
                print(f"  Unexpected error migrating {model_name} ID {record.id}: {e}")
                traceback.print_exc()
                continue
        
        # Final commit
        session_postgres.commit()
        
        print(f"\n  ✓ Migrated: {migrated}")
        print(f"  ⊘ Skipped (already exists): {skipped}")
        print(f"  ✗ Errors: {errors}")
        print(f"  Total: {total}")
        
        return migrated
        
    except Exception as e:
        session_postgres.rollback()
        print(f"  ✗ Fatal error migrating {model_name}: {e}")
        traceback.print_exc()
        return 0


def main():
    """Main migration function"""
    print("="*60)
    print("SQLite to PostgreSQL Migration Script")
    print("="*60)
    
    # Create Flask app context
    app = create_app('default')
    
    with app.app_context():
        # Get database URLs
        sqlite_uri = 'sqlite:///nikofree.db'
        
        # PostgreSQL connection from environment variables
        pg_host = os.getenv('PGHOST', 'localhost')
        pg_port = os.getenv('PGPORT', '5432')
        pg_user = os.getenv('PGUSER', 'postgres')
        pg_password = os.getenv('PGPASSWORD', '')
        pg_database = os.getenv('PGDATABASE', 'postgres')
        
        if not all([pg_host, pg_user, pg_database]):
            print("\n✗ Error: PostgreSQL environment variables not set!")
            print("Please set: PGHOST, PGUSER, PGDATABASE, PGPASSWORD")
            sys.exit(1)
        
        # URL-encode password to handle special characters like @, !, etc.
        pg_user_encoded = quote_plus(pg_user)
        pg_password_encoded = quote_plus(pg_password)
        pg_database_encoded = quote_plus(pg_database)
        
        postgres_uri = f"postgresql://{pg_user_encoded}:{pg_password_encoded}@{pg_host}:{pg_port}/{pg_database_encoded}"
        
        print(f"\nSQLite Database: {sqlite_uri}")
        print(f"PostgreSQL Database: {pg_host}:{pg_port}/{pg_database}")
        
        # Confirm before proceeding
        response = input("\nProceed with migration? This will add data to PostgreSQL (y/n): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            sys.exit(0)
        
        # Create engines
        print("\nConnecting to databases...")
        try:
            sqlite_engine = create_engine(sqlite_uri, echo=False)
            postgres_engine = create_engine(postgres_uri, echo=False)
            
            # Test connections
            sqlite_engine.connect()
            print("  ✓ Connected to SQLite")
            
            postgres_engine.connect()
            print("  ✓ Connected to PostgreSQL")
            
        except Exception as e:
            print(f"\n✗ Error connecting to databases: {e}")
            sys.exit(1)
        
        # Create sessions
        SessionSQLite = sessionmaker(bind=sqlite_engine)
        SessionPostgres = sessionmaker(bind=postgres_engine)
        
        session_sqlite = SessionSQLite()
        session_postgres = SessionPostgres()
        
        try:
            # First, ensure PostgreSQL schema is up to date
            print("\n" + "="*60)
            print("Creating/Updating PostgreSQL Schema...")
            print("="*60)
            
            # Create all tables in PostgreSQL
            db.Model.metadata.create_all(postgres_engine)
            print("  ✓ PostgreSQL schema ready")
            
            # Migrate tables in dependency order
            print("\n" + "="*60)
            print("Starting Data Migration...")
            print("="*60)
            
            total_migrated = 0
            
            for model_class in MODEL_ORDER:
                model_name = model_class.__name__
                migrated = migrate_table(session_sqlite, session_postgres, model_class, model_name)
                total_migrated += migrated
            
            print("\n" + "="*60)
            print("Migration Complete!")
            print("="*60)
            print(f"Total records migrated: {total_migrated}")
            print("\n✓ Migration successful!")
            print("\nNext steps:")
            print("1. Update your .env file to use PostgreSQL")
            print("2. Set DATABASE_URL or PostgreSQL environment variables")
            print("3. Restart your application")
            print("4. Verify data in PostgreSQL database")
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            traceback.print_exc()
            session_postgres.rollback()
            sys.exit(1)
        
        finally:
            session_sqlite.close()
            session_postgres.close()
            print("\nDatabase connections closed.")


if __name__ == '__main__':
    main()

