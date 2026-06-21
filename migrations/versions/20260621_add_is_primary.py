"""Add is_primary to control_types

Revision ID: 20260621_is_primary
Revises: 20260611_dba_cascade
Create Date: 2026-06-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20260621_is_primary'
# Указываем ID вашей последней актуальной миграции из базы
down_revision: Union[str, None] = '20260611_dba_cascade' 
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Добавляем колонку с дефолтным значением false, чтобы существующие записи не сломались
    op.add_column(
        'control_types', 
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )

def downgrade() -> None:
    op.drop_column('control_types', 'is_primary')