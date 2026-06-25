from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src.core.base_model import Base


class EducationalLevel(Base):
    """Уровни образования (бакалавриат, магистратура, аспирантура, специалитет)."""
    __tablename__ = 'educational_levels'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name_in_genetive: Mapped[str] = mapped_column(String(255), nullable=False)
