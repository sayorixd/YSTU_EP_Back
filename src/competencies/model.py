from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.base_model import Base


class Competency(Base):
    """Компетенции."""
    __tablename__ = 'competencies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(511), nullable=False)
    competency_group_id: Mapped[int] = mapped_column(Integer, ForeignKey('competency_groups.id'))

    competency_group = relationship('CompetencyGroup', back_populates='competencies')
    indicators = relationship('Indicator', back_populates='competency', cascade='all, delete-orphan')