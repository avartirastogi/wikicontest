"""add_scoring_parameters

Revision ID: 549b0e507d5d
Revises: 1fa03cdd51b
Create Date: 2025-12-30 16:16:58
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql  # IMPORTANT

# revision identifiers, used by Alembic.
revision = '549b0e507d5d'
down_revision = '1fa03cdd51b'
branch_labels = None
depends_on = None


def upgrade():
    # Contest level scoring configuration
    op.add_column(
        'contests',
        sa.Column(
            'scoring_parameters',
            mysql.JSON(),
            nullable=True,
            comment='Weights for scoring parameters'
        )
    )

    # Submission level jury scores
    op.add_column(
        'submissions',
        sa.Column(
            'parameter_scores',
            mysql.JSON(),
            nullable=True,
            comment='Per-parameter jury scores and comments'
        )
    )


def downgrade():
    op.drop_column('submissions', 'parameter_scores')
    op.drop_column('contests', 'scoring_parameters')
