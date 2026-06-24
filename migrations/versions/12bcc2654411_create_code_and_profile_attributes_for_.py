"""Create code and profile attributes for directions table

Revision ID: 12bcc2654411
Revises: 69062d367a19
Create Date: 2026-06-21 04:01:06.257468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Table, Column, Integer, String, select
from sqlalchemy.sql import table, column

import re


# revision identifiers, used by Alembic.
revision: str = '12bcc2654411'
down_revision: Union[str, None] = '69062d367a19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    op.add_column("directions", Column("code", String(255), nullable=True))
    op.add_column("directions", Column("profile", String(255), nullable=True))

    directions_adhoc = table(
        "directions",
        column("id", Integer()),
        column("name", String(50)),
        column("code", String(255)),
        column("profile", String(255))
    )
    
    results = conn.execute(sa.text("SELECT id, name FROM directions"))
    
    update_data = []
    for id_, name in results:
        # 09.03.04 Программная инженерия
        # 1 группа|2 группа
        # Код     |Профиль
        reg_exp = r"^(\d\d\.\d\d\.\d\d)\s(.+)$"
        m = re.match(reg_exp, name)
        code = "01.01.01"
        profile = name
        if m is not None:
            code = m.group(1)
            profile = m.group(2)
        
        update_data.append({"direction_id": id_, "code": code, "profile": profile})

    stmt = directions_adhoc.update()\
           .where(directions_adhoc.c.id == sa.bindparam("direction_id"))\
           .values(
               code=sa.bindparam("code"),
               profile=sa.bindparam("profile")
            )
    conn.execute(stmt, update_data)

    op.alter_column('directions', 'code', nullable=False)
    op.alter_column('directions', 'profile', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("directions", "code")
    op.drop_column("directions", "profile")
