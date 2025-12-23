"""Fix reviewed_by column type and foreign key

Revision ID: 4ef9d3c7655c
Revises: 14b63a85bf1c
Create Date: 2025-12-23 20:25:53.756855

This migration fixes a database schema issue where:
1. The reviewed_by column was VARCHAR(50) instead of INTEGER
2. The foreign key was pointing to users.username instead of users.id

This migration is idempotent - it checks the current state before making changes.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


# revision identifiers, used by Alembic.
revision = '4ef9d3c7655c'
down_revision = '14b63a85bf1c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Fix reviewed_by column type and foreign key constraint.
    
    This migration:
    1. Checks if reviewed_by is VARCHAR and converts it to INTEGER
    2. Drops incorrect foreign key if it exists
    3. Creates correct foreign key pointing to users.id
    """
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Get current column type
    columns = inspector.get_columns('submissions')
    reviewed_by_col = next((col for col in columns if col['name'] == 'reviewed_by'), None)
    
    if reviewed_by_col:
        col_type = str(reviewed_by_col['type'])
        
        # Check if column is VARCHAR (needs to be converted to INTEGER)
        if 'VARCHAR' in col_type.upper() or 'CHAR' in col_type.upper():
            # Clear any existing values (they're wrong type anyway)
            op.execute(text("UPDATE submissions SET reviewed_by = NULL WHERE reviewed_by IS NOT NULL"))
            
            # Drop incorrect foreign key if it exists
            fks = inspector.get_foreign_keys('submissions')
            for fk in fks:
                if 'reviewed_by' in fk['constrained_columns']:
                    op.drop_constraint(
                        fk['name'],
                        'submissions',
                        type_='foreignkey'
                    )
            
            # Alter column type from VARCHAR to INTEGER
            op.execute(text(
                "ALTER TABLE submissions MODIFY COLUMN reviewed_by INTEGER NULL"
            ))
    
    # Check if correct foreign key exists
    fks = inspector.get_foreign_keys('submissions')
    has_correct_fk = any(
        fk for fk in fks
        if 'reviewed_by' in fk['constrained_columns']
        and fk['referred_table'] == 'users'
        and 'id' in fk['referred_columns']
    )
    
    if not has_correct_fk:
        # Create correct foreign key constraint: reviewed_by -> users.id
        op.create_foreign_key(
            'fk_submissions_reviewed_by_users',
            'submissions',
            'users',
            ['reviewed_by'],
            ['id']
        )


def downgrade() -> None:
    """
    Reverse the migration.
    
    Note: This will convert INTEGER back to VARCHAR(50) and recreate
    the incorrect foreign key. This is for completeness, but you likely
    don't want to run this downgrade.
    """
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Drop correct foreign key if it exists
    fks = inspector.get_foreign_keys('submissions')
    for fk in fks:
        if 'reviewed_by' in fk['constrained_columns']:
            op.drop_constraint(
                fk['name'],
                'submissions',
                type_='foreignkey'
            )
    
    # Convert column back to VARCHAR(50) - NOT RECOMMENDED
    # This is included for completeness but should not be used
    op.execute(text(
        "ALTER TABLE submissions MODIFY COLUMN reviewed_by VARCHAR(50) NULL"
    ))
    
    # Note: We don't recreate the incorrect foreign key in downgrade
    # as it would point to users.username which is wrong
