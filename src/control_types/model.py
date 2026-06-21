from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.core.base_model import Base

class ControlType(Base):
    """Виды контроля дисциплин."""
    __tablename__ = 'control_types'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)