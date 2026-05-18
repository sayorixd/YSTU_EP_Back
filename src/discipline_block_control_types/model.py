from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base


class DisciplineBlockControlType(Base):
    __tablename__ = "discipline_block_control_types"

    id: Mapped[int] = mapped_column(primary_key=True)

    discipline_block_id: Mapped[int] = mapped_column(
        ForeignKey("discipline_blocks.id", ondelete="CASCADE")
    )

    control_type_id: Mapped[int] = mapped_column(
        ForeignKey("control_types.id", ondelete="CASCADE")
    )

    discipline_block = relationship(
        "DisciplineBlock",
        back_populates="control_types"
    )