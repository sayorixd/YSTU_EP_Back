"""Create the name_in_genetive attribute in the educational_levels table

Revision ID: 811ed42ecc3e
Revises: 12bcc2654411
Create Date: 2026-06-21 17:10:25.899637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Table, Column, Integer, String, select
from sqlalchemy.sql import table, column

import re


# revision identifiers, used by Alembic.
revision: str = '811ed42ecc3e'
down_revision: Union[str, None] = '12bcc2654411'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    op.add_column("educational_levels", Column("name_in_genetive", String(255), nullable=True))

    educational_levels_adhoc = table(
        "educational_levels",
        column("id", Integer()),
        column("name", String(20)),
        column("name_in_genetive", String(255))
    )
    
    results = conn.execute(sa.text("SELECT id, name FROM educational_levels"))
    
    update_data = []
    for id_, name in results:
        name_in_genetive = None
        if name == "Специалитет":
            name_in_genetive = "Специалитета"
        elif name == "Бакалавриат":
            name_in_genetive = "Бакалавриата"
        elif name == "Магистратура":
            name_in_genetive = "Магистратуры"
        elif name == "Аспирантура":
            name_in_genetive = "Аспирантуры"
        else:
            name_in_genetive = "default"
        
        update_data.append({"educational_level_id": id_, "name_in_genetive": name_in_genetive})

    stmt = educational_levels_adhoc.update()\
           .where(educational_levels_adhoc.c.id == sa.bindparam("educational_level_id"))\
           .values(
               name_in_genetive=sa.bindparam("name_in_genetive")
            )
    conn.execute(stmt, update_data)

    op.alter_column('educational_levels', 'name_in_genetive', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("educational_levels", "name_in_genetive")