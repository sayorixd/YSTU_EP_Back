"""Remove all incorrect discipline block competencies

Revision ID: 111339238cd1
Revises: 1ac59ff4bbc3
Create Date: 2026-06-24 03:32:52.515927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Table, Column, Integer, String, select, inspect
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '111339238cd1'
down_revision: Union[str, None] = '1ac59ff4bbc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    discipline_block_competency_table = table(
        "discipline_block_competencies",
        column("id", Integer()),
        column("discipline_block_id", Integer()),
        column("competency_id", Integer())
    )

    relationships = conn.execute(
        sa.text("SELECT * FROM discipline_block_competencies")
    ).mappings().all()

    delete_discipline_block_competency_ids = []
    for relationship in relationships:
        discipline_block_id = relationship["discipline_block_id"]
        competency_id = relationship["competency_id"]

        competency = conn.execute(
            sa.text(f"SELECT * FROM competencies WHERE id = {competency_id}")
        ).mappings().first()
        direction_id1 = competency["direction_id"]

        discipline_block = conn.execute(
            sa.text(f"SELECT * FROM discipline_blocks WHERE id = {discipline_block_id}")
        ).mappings().first()
        map_core = conn.execute(
            sa.text(f"SELECT * FROM map_cors WHERE id = {discipline_block["map_core_id"]}")
        ).mappings().first()
        direction_map_core = conn.execute(
            sa.text(f"SELECT * FROM direction_map_cors WHERE map_core_id = {map_core["id"]}")
        ).mappings().first()
        direction_id2 = direction_map_core["direction_id"]

        if direction_id1 != direction_id2:
            delete_discipline_block_competency_ids.append(relationship["id"])

    stmt = discipline_block_competency_table.delete()\
           .where(discipline_block_competency_table.c.id.in_(delete_discipline_block_competency_ids))
    conn.execute(stmt)


def downgrade() -> None:
    """Downgrade schema."""
    pass
