from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base


class Indicator(Base):
    __tablename__ = 'indicators'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(511), nullable=False)

    competency_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('competencies.id'),
        nullable=False,
    )

    competency = relationship('Competency', back_populates='indicators')