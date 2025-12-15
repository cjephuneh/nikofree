"""Add feedback and contact_messages tables

Revision ID: add_feedback_contact
Revises: b4b96fc5b6ff
Create Date: 2025-12-15 13:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_feedback_contact'
down_revision = 'b4b96fc5b6ff'
branch_labels = None
depends_on = None


def upgrade():
    # Check if tables exist before creating them
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Create feedback table
    if 'feedback' not in existing_tables:
        op.create_table('feedback',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('feedback_type', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=True, server_default=sa.text('false')),
    sa.Column('is_starred', sa.Boolean(), nullable=True, server_default=sa.text('false')),
    sa.Column('is_archived', sa.Boolean(), nullable=True, server_default=sa.text('false')),
    sa.Column('read_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
        op.create_index('ix_feedback_created_at', 'feedback', ['created_at'], unique=False)

    # Create contact_messages table
    if 'contact_messages' not in existing_tables:
        op.create_table('contact_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('subject', sa.String(length=200), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=True, server_default=sa.text('false')),
    sa.Column('is_starred', sa.Boolean(), nullable=True, server_default=sa.text('false')),
    sa.Column('is_archived', sa.Boolean(), nullable=True, server_default=sa.text('false')),
    sa.Column('read_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
        op.create_index('ix_contact_messages_created_at', 'contact_messages', ['created_at'], unique=False)


def downgrade():
    # Drop contact_messages table
    op.drop_index('ix_contact_messages_created_at', table_name='contact_messages')
    op.drop_table('contact_messages')

    # Drop feedback table
    op.drop_index('ix_feedback_created_at', table_name='feedback')
    op.drop_table('feedback')

