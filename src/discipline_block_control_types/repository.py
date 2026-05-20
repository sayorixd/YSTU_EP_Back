from sqlalchemy.orm import Session
from src.core.sqlalchemy_repository import SQLAlchemyRepository
from .model import DisciplineBlockControlType


class DisciplineBlockControlTypesRepository(
    SQLAlchemyRepository[DisciplineBlockControlType]
):
    def __init__(self, session):
        super().__init__(session, DisciplineBlockControlType)