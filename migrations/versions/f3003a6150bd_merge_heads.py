"""Merge heads

Revision ID: f3003a6150bd
Revises: 111339238cd1, 20260622_final_cleanup
Create Date: 2026-06-24 06:57:52.362716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3003a6150bd'
down_revision: Union[str, None] = ('111339238cd1', '20260622_final_cleanup')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
