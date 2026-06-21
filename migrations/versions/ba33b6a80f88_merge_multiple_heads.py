"""merge_multiple_heads

Revision ID: ba33b6a80f88
Revises: 20260618_add_is_main, 20260621_is_primary
Create Date: 2026-06-21 15:20:16.151225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba33b6a80f88'
down_revision: Union[str, None] = ('20260618_add_is_main', '20260621_is_primary')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
