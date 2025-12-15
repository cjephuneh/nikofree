"""add_rejection_reasons_table_and_partner_fields

Revision ID: 1aae8dc98cf6
Revises: add_feedback_contact
Create Date: 2025-12-15 19:59:31.189834

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '1aae8dc98cf6'
down_revision = 'add_feedback_contact'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Create rejection_reasons table
    if 'rejection_reasons' not in existing_tables:
        op.create_table('rejection_reasons',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Add new columns to partners table
    partners_columns = [col['name'] for col in inspector.get_columns('partners')]
    
    if 'rejection_reason_id' not in partners_columns:
        op.add_column('partners', sa.Column('rejection_reason_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_partners_rejection_reason', 'partners', 'rejection_reasons', ['rejection_reason_id'], ['id'])
    
    if 'internal_rejection_note' not in partners_columns:
        op.add_column('partners', sa.Column('internal_rejection_note', sa.Text(), nullable=True))
    
    # Seed rejection reasons
    rejection_reasons_table = sa.table('rejection_reasons',
        sa.column('id', sa.Integer),
        sa.column('title', sa.String),
        sa.column('description', sa.Text),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )
    
    from datetime import datetime
    now = datetime.utcnow()
    
    op.bulk_insert(rejection_reasons_table, [
        {
            'title': 'Incomplete or Insufficient Information',
            'description': 'The partner did not provide all required application details (e.g., missing contact info, business description, ID verification, tax or registration documents), making it impossible to assess their eligibility.',
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'title': 'Does Not Meet Eligibility Criteria',
            'description': "The applicant's profile or business category does not align with our platform's requirements (e.g., ineligible services, geographical restrictions, or lack of relevant industry experience).",
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'title': 'Unable to Verify Identity or Credentials',
            'description': "We were unable to verify the applicant's identity, business legitimacy, or required certifications (e.g., inconsistent information, unverifiable documents, or lack of a professional online presence).",
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'title': 'Policy or Compliance Conflicts',
            'description': "The applicant's practices, terms, or offerings conflict with our platform policies, legal standards, or community guidelines (e.g., non-compliance with data protection laws, prohibited services, or ethical concerns).",
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'title': 'Incompatible Business Category',
            'description': "The partner's business does not fit into any of our supported categories or market segments, making integration with our platform impractical.",
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }
    ])


def downgrade():
    # Remove columns from partners table
    op.drop_constraint('fk_partners_rejection_reason', 'partners', type_='foreignkey')
    op.drop_column('partners', 'internal_rejection_note')
    op.drop_column('partners', 'rejection_reason_id')
    
    # Drop rejection_reasons table
    op.drop_table('rejection_reasons')
