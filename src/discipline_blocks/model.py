from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.base_model import Base

class DisciplineBlock(Base):
    __tablename__ = 'discipline_blocks'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discipline_id: Mapped[int] = mapped_column(Integer, ForeignKey('disciplines.id'))
    credit_units: Mapped[int] = mapped_column(Integer, nullable=False)
    control_type_id: Mapped[int] = mapped_column(Integer, ForeignKey('control_types.id'))
    lecture_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    practice_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    lab_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    semester_number: Mapped[int] = mapped_column(Integer, nullable=False)
    map_core_id: Mapped[int] = mapped_column(Integer, ForeignKey('map_cors.id', ondelete='CASCADE'))
    
    map_core = relationship('MapCore', back_populates='discipline_blocks', foreign_keys=[map_core_id])
    
    # Связь с дополнительными видами контроля
    secondary_control_links = relationship(
        "DisciplineBlockControlType",
        back_populates="discipline_block",
        cascade="all, delete-orphan"
    )