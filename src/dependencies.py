from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated, Generator
from src.database import engine

# Импорты репозиториев
from src.discipline_block_control_types.repository import DisciplineBlockControlTypesRepository
from src.directions.repository import DirectionsRepository
from src.map_cors.repository import MapCorsRepository
from src.direction_map_cors.repository import DirectionMapCorsRepository
from src.discipline_blocks.repository import DisciplineBlocksRepository
from src.discipline_block_competencies.repository import DisciplineBlockCompetenciesRepository
from src.disciplines.repository import DisciplinesRepository
from src.departments.repository import DepartmentsRepository
from src.control_types.repository import ControlTypesRepository
from src.competencies.repository import CompetenciesRepository
from src.maps.service import MapsService
from src.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def get_session() -> Generator[Session, None, None]:  # <-- Изменить аннотацию
    with Session(autoflush=False, bind=engine) as session:
        yield session
    
SessionDep = Annotated[Session, Depends(get_session)]

def get_directions_repository(session: SessionDep) -> DirectionsRepository:
    return DirectionsRepository(session)
DirectionsRepositoryDep = Annotated[DirectionsRepository, Depends(get_directions_repository)]

def get_map_cors_repository(session: SessionDep) -> MapCorsRepository:
    return MapCorsRepository(session)
MapCorsRepositoryDep = Annotated[MapCorsRepository, Depends(get_map_cors_repository)]

def get_direction_map_cors_repository(session: SessionDep) -> DirectionMapCorsRepository:
    return DirectionMapCorsRepository(session)
DirectionMapCorsRepositoryDep = Annotated[DirectionMapCorsRepository, Depends(get_direction_map_cors_repository)]

def get_discipline_blocks_repository(session: SessionDep) -> DisciplineBlocksRepository:
    return DisciplineBlocksRepository(session)
DisciplineBlocksRepositoryDep = Annotated[DisciplineBlocksRepository, Depends(get_discipline_blocks_repository)]

def get_discipline_block_competencies_repository(session: SessionDep) -> DisciplineBlockCompetenciesRepository:
    return DisciplineBlockCompetenciesRepository(session)
DisciplineBlockCompetenciesRepositoryDep = Annotated[
    DisciplineBlockCompetenciesRepository, Depends(get_discipline_block_competencies_repository)
]

def get_discipline_block_control_types_repository(session: SessionDep) -> DisciplineBlockControlTypesRepository:
    return DisciplineBlockControlTypesRepository(session)
    
DisciplineBlockControlTypesRepositoryDep = Annotated[
    DisciplineBlockControlTypesRepository, Depends(get_discipline_block_control_types_repository)
]

def get_disciplines_repository(session: SessionDep) -> DisciplinesRepository:
    return DisciplinesRepository(session)
DisciplinesRepositoryDep = Annotated[DisciplinesRepository, Depends(get_disciplines_repository)]

def get_departments_repository(session: SessionDep) -> DepartmentsRepository:
    return DepartmentsRepository(session)
DepartmentsRepositoryDep = Annotated[DepartmentsRepository, Depends(get_departments_repository)]

def get_control_types_repository(session: SessionDep) -> ControlTypesRepository:
    return ControlTypesRepository(session)
ControlTypesRepositoryDep = Annotated[ControlTypesRepository, Depends(get_control_types_repository)]

def get_competencies_repository(session: SessionDep) -> CompetenciesRepository:
    return CompetenciesRepository(session)
CompetenciesRepositoryDep = Annotated[CompetenciesRepository, Depends(get_competencies_repository)]

# --- Сервис карт ---
# src/dependencies.py

def get_maps_service(
    directions_repository: DirectionsRepositoryDep,
    map_cors_repository: MapCorsRepositoryDep,
    direction_map_cors_repository: DirectionMapCorsRepositoryDep,
    discipline_blocks_repository: DisciplineBlocksRepositoryDep,
    discipline_block_competencies_repository: DisciplineBlockCompetenciesRepositoryDep,
    discipline_block_control_types_repository: DisciplineBlockControlTypesRepositoryDep,
    disciplines_repository: DisciplinesRepositoryDep,
    departments_repository: DepartmentsRepositoryDep,
    control_types_repository: ControlTypesRepositoryDep,
    competencies_repository: CompetenciesRepositoryDep
) -> MapsService:
    return MapsService(
        directions_repository=directions_repository,
        map_cors_repository=map_cors_repository,
        direction_map_cors_repository=direction_map_cors_repository,
        discipline_blocks_repository=discipline_blocks_repository,
        discipline_block_competencies_repository=discipline_block_competencies_repository,
        disciplines_repository=disciplines_repository,
        departments_repository=departments_repository,
        control_types_repository=control_types_repository,
        competencies_repository=competencies_repository,
        discipline_block_control_types_repository=discipline_block_control_types_repository
    )

MapsServiceDep = Annotated[MapsService, Depends(get_maps_service)]