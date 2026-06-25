"""Make competencies specific to directions

Revision ID: 1ac59ff4bbc3
Revises: 811ed42ecc3e
Create Date: 2026-06-21 23:26:54.179850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Table, Column, Integer, String, select, inspect
from sqlalchemy.sql import table, column

import re


# revision identifiers, used by Alembic.
revision: str = '1ac59ff4bbc3'
down_revision: Union[str, None] = '811ed42ecc3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    directions_adhoc = table(
        "directions",
        column("id", Integer())
    )
    competencies_adhoc = table(
        "competencies",
        column("id", Integer()),
        column("code", String(10)),
        column("name", String(255)),
        column("description", String(511)),
        column("competency_group_id", Integer()),
        column("direction_id", Integer())
    )

    op.drop_constraint("competencies_code_key", "competencies")

    # Get ids of directions
    direction_ids = conn.execute(
        sa.text("SELECT id FROM directions")
    ).scalars().all()
    if len(direction_ids) == 0:
        raise Exception("No directions to attach competencies to")

    op.add_column("competencies", Column("direction_id", Integer(), nullable=True))

    # Set competencies' direction_id attribute to the id of the first direction
    competencies = conn.execute(
        sa.text("SELECT * FROM competencies")
    ).mappings().all()
    update_data = [
        {
            "competency_id": competency["id"],
            "direction_id": direction_ids[0]
        }
        for competency in competencies
    ]
    stmt = competencies_adhoc.update()\
           .where(competencies_adhoc.c.id == sa.bindparam("competency_id"))\
           .values({ "direction_id": sa.bindparam("direction_id") })
    conn.execute(stmt, update_data)

    # Copy competencies to other directions
    insert_data = []
    for i in range(1, len(direction_ids)):
        direction_id = direction_ids[i]
        for competency in competencies:
            insert_data.append({
                "code": competency["code"],
                "name": competency["name"],
                "description": competency["description"],
                "competency_group_id": competency["competency_group_id"],
                "direction_id": direction_id
            })

    op.bulk_insert(competencies_adhoc, insert_data)
    
    op.create_foreign_key(
        "fk_direction_id_competencies",
        "competencies",
        "directions",
        ["direction_id"],
        ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    competencies_adhoc = table(
        "competencies",
        column("id", Integer()),
        column("code", String(10)),
        column("name", String(255)),
        column("description", String(511)),
        column("competency_group_id", Integer()),
        column("direction_id", Integer())
    )

    competencies = conn.execute(
        sa.text("SELECT * FROM competencies")
    ).mappings().all()

    min_direction_id = min([competency["direction_id"] for competency in competencies])
    delete_competency_ids = [
        competency["id"]
        for competency in competencies
        if competency["direction_id"] != min_direction_id
    ]

    stmt = competencies_adhoc.delete()\
           .where(competencies_adhoc.c.id.in_(delete_competency_ids))
    conn.execute(stmt)

    op.drop_constraint("fk_direction_id_competencies", "competencies", type_="foreignkey")
    op.drop_column("competencies", "direction_id")
    op.create_unique_constraint("competencies_code_key", "competencies", ["code"])
