"""add withdrawal_fee to partner_payouts

Revision ID: add_withdrawal_fee
Revises: 1aae8dc98cf6
Create Date: 2025-12-17 12:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_withdrawal_fee'
down_revision = '1aae8dc98cf6'
branch_labels = None
depends_on = None


def upgrade():
    # Add withdrawal_fee column to partner_payouts table
    op.add_column('partner_payouts', 
                  sa.Column('withdrawal_fee', sa.Numeric(10, 2), nullable=True, server_default='0.00'))


def downgrade():
    # Remove withdrawal_fee column
    op.drop_column('partner_payouts', 'withdrawal_fee')

