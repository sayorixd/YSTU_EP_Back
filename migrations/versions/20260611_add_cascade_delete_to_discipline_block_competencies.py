"""Add cascade delete to discipline_block_competencies foreign key

Revision ID: 20260611_cascade_delete_discipline_block_competencies
Revises: 20260607_cascade_delete
Create Date: 2026-06-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260611_dbc_cascade'
down_revision: Union[str, None] = '20260607_cascade_delete'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        'discipline_block_competencies_discipline_block_id_fkey',
        'discipline_block_competencies',
        type_='foreignkey'
    )
    op.create_foreign_key(
        'discipline_block_competencies_discipline_block_id_fkey',
        'discipline_block_competencies',
        'discipline_blocks',
        ['discipline_block_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'discipline_block_competencies_discipline_block_id_fkey',
        'discipline_block_competencies',
        type_='foreignkey'
    )
    op.create_foreign_key(
        'discipline_block_competencies_discipline_block_id_fkey',
        'discipline_block_competencies',
        'discipline_blocks',
        ['discipline_block_id'],
        ['id']
    )
