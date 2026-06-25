from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.base_model import Base


class CompetencyGroup(Base):
    """Группы компетенций."""
    __tablename__ = 'competency_groups'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    short_name: Mapped[str] = mapped_column(String(255), nullable=False)

    competencies = relationship('Competency', back_populates='competency_group', cascade='all, delete-orphan')
