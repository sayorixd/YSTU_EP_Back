from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.core.base_model import Base


class DisciplineBlockActivityType(Base):
    """Связи блоков дисциплин и видов учебных занятий."""
    __tablename__ = 'discipline_block_activity_types'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discipline_block_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('discipline_blocks.id', ondelete='CASCADE')
    )
    activity_type_id: Mapped[int] = mapped_column(Integer, ForeignKey('activity_types.id'))
