"""Add byte count range fields to contests

Revision ID: 51004fa44a6b
Revises: fc55a0c85ffc
Create Date: 2025-12-21 07:23:55.291006

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '51004fa44a6b'
down_revision = 'fc55a0c85ffc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add byte count range fields to contests table
    # These fields define the allowed byte count range for article submissions
    # None means no limit (no minimum or no maximum)
    op.add_column('contests', sa.Column('min_byte_count', sa.Integer(), nullable=True))
    op.add_column('contests', sa.Column('max_byte_count', sa.Integer(), nullable=True))
    
    # Remove old required_bytes column if it exists (legacy field, no longer used)
    op.drop_column('contests', 'required_bytes')


def downgrade() -> None:
    # Reverse the migration: remove new fields and restore old field
    op.add_column('contests', sa.Column('required_bytes', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('contests', 'max_byte_count')
    op.drop_column('contests', 'min_byte_count')

