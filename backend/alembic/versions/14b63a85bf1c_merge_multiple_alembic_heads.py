"""merge multiple alembic heads

Revision ID: 14b63a85bf1c
Revises: 51004fa44a6b, ccd6aa4c2144
Create Date: 2025-12-23 19:33:45.250420

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14b63a85bf1c'
down_revision = ('51004fa44a6b', 'ccd6aa4c2144')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

