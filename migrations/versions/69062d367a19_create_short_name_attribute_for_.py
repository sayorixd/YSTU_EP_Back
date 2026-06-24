"""Create short name attribute for competency groups

Revision ID: 69062d367a19
Revises: 20260611_dba_cascade
Create Date: 2026-06-18 13:54:32.575916

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Table, Column, Integer, String, select
from sqlalchemy.sql import table, column

import re


# revision identifiers, used by Alembic.
revision: str = '69062d367a19'
down_revision: Union[str, None] = '20260611_dba_cascade'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    op.add_column("competency_groups", Column("short_name", String(255), nullable=True))

    competency_group_adhoc = table(
        "competency_groups",
        column("id", Integer()),
        column("name", String(255)),
        column("short_name", String(255))
    )
    
    results = conn.execute(sa.text("SELECT id, name FROM competency_groups"))
    
    update_data = []
    for id_, name in results:
        # Общекультурные компетенции (ОК) - группа 1 - полное название группы компетенций
        reg_exp = r"^(.+)\s\((\w+)\)$"
        m = re.match(reg_exp, name)
        full_name = None
        short_name = None
        if m is None:
            full_name = name
            short_name = name
        else:
            full_name = m.group(1)
            short_name = m.group(2)
        update_data.append({"competency_group_id": id_, "full_name": full_name, "short_name": short_name})
        
    stmt = competency_group_adhoc.update()\
           .where(competency_group_adhoc.c.id == sa.bindparam("competency_group_id"))\
           .values(
               name=sa.bindparam("full_name"),
               short_name=sa.bindparam("short_name")
            )
    conn.execute(stmt, update_data)

    op.alter_column('competency_groups', 'short_name', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("competency_groups", "short_name")
