"""remove_max_byte_count_from_contests

Revision ID: a1b2c3d4e5f6
Revises: 81e35234e74d
Create Date: 2025-12-29 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '81e35234e74d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop max_byte_count column from contests table
    # Check if column exists before dropping to handle partial migration scenarios
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('contests')]
    
    if 'max_byte_count' in columns:
        op.drop_column('contests', 'max_byte_count')
    
    # Make min_byte_count required (NOT NULL)
    # First, set a default value for any existing NULL values
    # Then alter the column to be NOT NULL
    from sqlalchemy import text
    
    # Update any NULL values to 0
    conn.execute(text("UPDATE contests SET min_byte_count = 0 WHERE min_byte_count IS NULL"))
    
    # For MySQL, use MODIFY COLUMN syntax which is more reliable
    # Check database dialect to use appropriate syntax
    dialect_name = conn.dialect.name
    if dialect_name == 'mysql':
        conn.execute(text("ALTER TABLE contests MODIFY COLUMN min_byte_count INTEGER NOT NULL"))
    else:
        # For other databases, use standard alter_column
        op.alter_column('contests', 'min_byte_count',
                        existing_type=sa.Integer(),
                        nullable=False,
                        existing_nullable=True)


def downgrade() -> None:
    # Make min_byte_count optional again (nullable)
    op.alter_column('contests', 'min_byte_count',
                    existing_type=sa.Integer(),
                    nullable=True,
                    existing_nullable=False)
    
    # Restore max_byte_count column
    op.add_column('contests', sa.Column('max_byte_count', sa.Integer(), nullable=True))

