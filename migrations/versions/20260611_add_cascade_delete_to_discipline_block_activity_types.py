"""Add cascade delete to discipline_block_activity_types foreign key

Revision ID: 20260611_cascade_delete_discipline_block_activity_types
Revises: 20260611_cascade_delete_discipline_block_competencies
Create Date: 2026-06-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260611_dba_cascade'
down_revision: Union[str, None] = '20260611_dbc_cascade'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        'discipline_block_activity_types_discipline_block_id_fkey',
        'discipline_block_activity_types',
        type_='foreignkey'
    )
    op.create_foreign_key(
        'discipline_block_activity_types_discipline_block_id_fkey',
        'discipline_block_activity_types',
        'discipline_blocks',
        ['discipline_block_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'discipline_block_activity_types_discipline_block_id_fkey',
        'discipline_block_activity_types',
        type_='foreignkey'
    )
    op.create_foreign_key(
        'discipline_block_activity_types_discipline_block_id_fkey',
        'discipline_block_activity_types',
        'discipline_blocks',
        ['discipline_block_id'],
        ['id']
    )
