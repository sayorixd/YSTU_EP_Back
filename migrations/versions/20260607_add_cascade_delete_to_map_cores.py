"""Add cascade delete to map_cores foreign keys

Revision ID: 20260607_cascade_delete
Revises: 1b5ad9a8057d
Create Date: 2026-06-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260607_cascade_delete'
down_revision: Union[str, None] = '1b5ad9a8057d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop existing foreign keys without cascade delete
    op.drop_constraint('discipline_blocks_map_core_id_fkey', 'discipline_blocks', type_='foreignkey')
    op.drop_constraint('direction_map_cors_map_core_id_fkey', 'direction_map_cors', type_='foreignkey')
    
    # Create new foreign keys with cascade delete
    op.create_foreign_key(
        'discipline_blocks_map_core_id_fkey',
        'discipline_blocks',
        'map_cors',
        ['map_core_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'direction_map_cors_map_core_id_fkey',
        'direction_map_cors',
        'map_cors',
        ['map_core_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign keys with cascade delete
    op.drop_constraint('discipline_blocks_map_core_id_fkey', 'discipline_blocks', type_='foreignkey')
    op.drop_constraint('direction_map_cors_map_core_id_fkey', 'direction_map_cors', type_='foreignkey')
    
    # Recreate foreign keys without cascade delete
    op.create_foreign_key(
        'discipline_blocks_map_core_id_fkey',
        'discipline_blocks',
        'map_cors',
        ['map_core_id'],
        ['id']
    )
    op.create_foreign_key(
        'direction_map_cors_map_core_id_fkey',
        'direction_map_cors',
        'map_cors',
        ['map_core_id'],
        ['id']
    )
