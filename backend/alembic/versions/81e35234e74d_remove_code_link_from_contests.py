"""remove_code_link_from_contests

Revision ID: 81e35234e74d
Revises: eb62079dd965
Create Date: 2025-12-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '81e35234e74d'
down_revision = 'eb62079dd965'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop code_link column from contests table
    # Check if column exists before dropping to handle partial migration scenarios
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('contests')]
    
    if 'code_link' in columns:
        op.drop_column('contests', 'code_link')


def downgrade() -> None:
    # Restore code_link column
    op.add_column('contests', sa.Column('code_link', sa.String(length=500), nullable=True))

