"""increase lengths to 511

Revision ID: 1b5ad9a8057d
Revises: 4a9fc1b3b128
Create Date: 2026-06-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "1b5ad9a8057d"
down_revision: Union[str, None] = "4a9fc1b3b128"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column(
        "competencies",
        "description",
        existing_type=sa.String(length=255),
        type_=sa.String(length=511),
        existing_nullable=False,
    )

    op.alter_column(
        "indicators",
        "name",
        existing_type=sa.String(length=255),
        type_=sa.String(length=511),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "competencies",
        "description",
        existing_type=sa.String(length=511),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

    op.alter_column(
        "indicators",
        "name",
        existing_type=sa.String(length=511),
        type_=sa.String(length=255),
        existing_nullable=False,
    )