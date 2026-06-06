from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src.core.base_model import Base


class EducationalForm(Base):
    """Формы образования (очная, заочная, очно-заочная)."""
    __tablename__ = 'educational_forms'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(63), nullable=False, unique=True)