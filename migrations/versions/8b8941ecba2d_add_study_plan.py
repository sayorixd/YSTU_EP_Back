"""add study plan

Revision ID: 8b8941ecba2d
Revises: 20260516_short_name_nullable
Create Date: 2026-05-17 16:35:30.846450
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8b8941ecba2d'
down_revision: Union[str, None] = '20260516_short_name_nullable'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'study_plan',

        sa.Column(
            'id',
            sa.BigInteger(),
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            'educational_plan_id',
            sa.BigInteger(),
            nullable=False
        ),

        sa.Column(
            'name',
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            'data',
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False
        ),

        sa.Column(
            'created_at',
            sa.DateTime(
                timezone=True
            ),
            server_default=sa.text(
                'now()'
            ),
            nullable=True
        ),

        sa.Column(
            'updated_at',
            sa.DateTime(
                timezone=True
            ),
            server_default=sa.text(
                'now()'
            ),
            nullable=True
        ),

        sa.PrimaryKeyConstraint(
            'id'
        )
    )


def downgrade() -> None:
    op.drop_table(
        'study_plan'
    )