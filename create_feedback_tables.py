#!/usr/bin/env python3
"""
Simple script to create feedback and contact_messages tables
Run this with: python create_feedback_tables.py
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Get database URL from environment or config
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Try to construct from individual vars
    pg_host = os.getenv('PGHOST', 'localhost')
    pg_port = os.getenv('PGPORT', '5432')
    pg_user = os.getenv('PGUSER', 'postgres')
    pg_password = os.getenv('PGPASSWORD', '')
    pg_database = os.getenv('PGDATABASE', 'postgres')
    
    if pg_host and pg_user and pg_database:
        from urllib.parse import quote_plus
        pg_user_encoded = quote_plus(pg_user)
        pg_password_encoded = quote_plus(pg_password)
        pg_database_encoded = quote_plus(pg_database)
        database_url = f"postgresql://{pg_user_encoded}:{pg_password_encoded}@{pg_host}:{pg_port}/{pg_database_encoded}"
    else:
        print("Error: DATABASE_URL or PostgreSQL environment variables not set")
        sys.exit(1)

# Create engine
engine = create_engine(database_url)

# SQL to create tables
create_feedback_table = """
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    email VARCHAR(120),
    feedback_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    rating INTEGER,
    is_read BOOLEAN DEFAULT false,
    is_starred BOOLEAN DEFAULT false,
    is_archived BOOLEAN DEFAULT false,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_feedback_created_at ON feedback(created_at);
"""

create_contact_messages_table = """
CREATE TABLE IF NOT EXISTS contact_messages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(120) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT false,
    is_starred BOOLEAN DEFAULT false,
    is_archived BOOLEAN DEFAULT false,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_contact_messages_created_at ON contact_messages(created_at);
"""

try:
    with engine.connect() as conn:
        print("Creating feedback table...")
        conn.execute(text(create_feedback_table))
        conn.commit()
        print("✓ Feedback table created")
        
        print("Creating contact_messages table...")
        conn.execute(text(create_contact_messages_table))
        conn.commit()
        print("✓ Contact messages table created")
        
        print("\n✅ All tables created successfully!")
        
except ProgrammingError as e:
    if "already exists" in str(e):
        print("⚠️  Tables already exist, skipping creation")
    else:
        print(f"❌ Error: {e}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)



