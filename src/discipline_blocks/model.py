from sqlalchemy import Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base


class DisciplineBlock(Base):
    """Блоки дисциплин."""
    __tablename__ = 'discipline_blocks'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    discipline_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('disciplines.id')
    )

    credit_units: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # временно оставляем
    control_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('control_types.id')
    )

    lecture_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    practice_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    lab_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    semester_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    map_core_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('map_cors.id')
    )

    has_course_work: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    has_course_project: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    has_rz: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    has_rgr: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    has_referat: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

