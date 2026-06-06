from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import Base


class DisciplineBlockCompetency(Base):
    """Связи блоков дисциплин и компетенций."""
    __tablename__ = 'discipline_block_competencies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discipline_block_id: Mapped[int] = mapped_column(Integer, ForeignKey('discipline_blocks.id'))
    competency_id: Mapped[int] = mapped_column(Integer, ForeignKey('competencies.id'))