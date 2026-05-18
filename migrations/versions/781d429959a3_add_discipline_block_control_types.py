"""add discipline block control types

Revision ID: 781d429959a3
Revises: 8b8941ecba2d
Create Date: 2026-05-17 16:46:06.301717
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '781d429959a3'
down_revision: Union[str, None] = '8b8941ecba2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'discipline_block_control_types',

        sa.Column(
            'id',
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            'discipline_block_id',
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            'control_type_id',
            sa.Integer(),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ['discipline_block_id'],
            ['discipline_blocks.id'],
            ondelete='CASCADE'
        ),

        sa.ForeignKeyConstraint(
            ['control_type_id'],
            ['control_types.id'],
            ondelete='CASCADE'
        ),

        sa.PrimaryKeyConstraint(
            'id'
        )
    )


def downgrade() -> None:
    op.drop_table(
        'discipline_block_control_types'
    )