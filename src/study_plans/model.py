from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    DateTime,
    func,
    Text
)

from sqlalchemy.dialects.postgresql import JSONB

from src.core.base_model import Base


class StudyPlan(Base):
    __tablename__ = "study_plan"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    educational_plan_id = Column(
        BigInteger,
        nullable=False
    )

    name = Column(
        Text,
        nullable=True
    )

    data = Column(
        JSONB,
        nullable=False,
        default={}
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )