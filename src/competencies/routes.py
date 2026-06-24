from fastapi import APIRouter, status, Path
from fastapi.responses import Response
from sqlalchemy import select, exists, and_
from typing import Annotated, Any
from src.dependencies import SessionDep
from src.exceptions import (
    CompetencyNotFoundException, CompetencyGroupNotFoundException, DirectionNotFoundException
)
from src.competency_groups.model import CompetencyGroup
from src.directions.model import Direction
from .model import Competency
from .schemas import CompetencyCreate, CompetencyUpdate, CompetencyRead

router = APIRouter(
    prefix='/competencies',
    tags=['competencies']
)


@router.get(
    '/{competency_id}',
    responses={
        200: {'description': 'Competency successfully received'},
        404: {'description': 'Competency not found'}
    },
    summary='Return the competency'
)
def get_competency(competency_id: Annotated[int, Path(gt=0)], session: SessionDep) -> CompetencyRead:
    """Return the competency with the specified id"""
    competency = session.get(Competency, competency_id)
    if not competency:
        raise CompetencyNotFoundException()
    return competency


@router.patch(
    '/{competency_id}',
    responses={
        200: {'description': 'Competency successfully updated'},
        404: {'description': 'Competency or competency group not found'},
        409: {'description': 'Competency data is not unique'}
    },
    summary='Update the competency'
)
def update_competency(
        competency_id: Annotated[int, Path(gt=0)], competency_data: CompetencyUpdate, session: SessionDep
) -> CompetencyRead:
    """Update the competency with the specified id with the given information (blank values are ignored)"""
    competency = session.get(Competency, competency_id)
    if not competency:
        raise CompetencyNotFoundException()

    if competency_data.competency_group_id:
        competency_group = session.get(CompetencyGroup, competency_data.competency_group_id)
        if not competency_group:
            raise CompetencyGroupNotFoundException()

    for key, value in competency_data.model_dump(exclude_none=True).items():
        setattr(competency, key, value)
    session.commit()
    session.refresh(competency)
    return competency


@router.delete(
    '/{competency_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Competency successfully deleted'},
        404: {'description': 'Competency not found'},
    },
    summary='Delete the competency'
)
def delete_competency(competency_id: Annotated[int, Path(gt=0)], session: SessionDep) -> Response:
    """Delete the competency with the specified id."""
    competency = session.get(Competency, competency_id)
    if not competency:
        raise CompetencyNotFoundException()
    session.delete(competency)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    '',
    responses={200: {'description': 'Competencies successfully received'}},
    summary='Return a list of competencies'
)
def get_competencies(session: SessionDep) -> list[CompetencyRead]:
    """Return a list of competencies."""
    competencies = session.execute(select(Competency)).scalars()
    return competencies


@router.get(
    '/direction/{direction_id}',
    responses={200: {'description': 'Competencies successfully received'}},
    summary='Return a list of competencies that are specific to the direction'
)
def get_competencies_of_direction(
    direction_id: Annotated[int, Path(gt=0)],
    session: SessionDep
) -> list[CompetencyRead]:
    """Return a list of competencies that are specific to the direction"""
    direction = session.get(Direction, direction_id)
    if not direction:
        raise DirectionNotFoundException()
    
    competencies = session.execute(
        select(Competency).where(Competency.direction_id == direction_id)
    ).scalars()

    return competencies


@router.post(
    '',
    response_model=CompetencyRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'Competency successfully created'},
        404: {'description': 'Competency group not found'},
        409: {'description': 'Competency data is not unique'}
    },
    summary='Create the competency'
)
def create_competency(competency_data: CompetencyCreate, session: SessionDep) -> Any:
    """Create the competency with the given information."""
    competency_group = session.get(CompetencyGroup, competency_data.competency_group_id)
    if not competency_group:
        raise CompetencyGroupNotFoundException()
    
    direction = session.get(Direction, competency_data.direction_id)
    if not direction:
        raise DirectionNotFoundException()

    competency = Competency(**competency_data.model_dump())
    session.add(competency)
    session.commit()
    session.refresh(competency)
    return competency
