"""Add is_main to control_types
Revision ID: 20260618_add_is_main
Revises: 20260611_dba_cascade
Create Date: 2026-06-18
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20260618_add_is_main'
down_revision: Union[str, None] = '20260611_dba_cascade'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('control_types', sa.Column('is_main', sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade() -> None:
    op.drop_column('control_types', 'is_main')