"""Add outreach_dashboard_url column to contests table

Revision ID: d55c876a1323
Revises: de4074ff4ff8
Create Date: 2026-01-30 17:47:10.503823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd55c876a1323'
down_revision = 'de4074ff4ff8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add outreach_dashboard_url column to contests table
    op.add_column('contests', sa.Column('outreach_dashboard_url', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove outreach_dashboard_url column from contests table
    op.drop_column('contests', 'outreach_dashboard_url')

