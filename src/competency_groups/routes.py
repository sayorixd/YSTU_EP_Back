from fastapi import APIRouter, status, Path
from fastapi.responses import Response
from sqlalchemy import select, exists, and_
from typing import Annotated, Any
from src.dependencies import SessionDep
from src.exceptions import CompetencyGroupNotFoundException, CompetencyGroupNameIsNotUniqueException
from .model import CompetencyGroup
from .schemas import CompetencyGroupCreate, CompetencyGroupUpdate, CompetencyGroupRead

router = APIRouter(
    prefix='/competency-groups',
    tags=['competency groups']
)


@router.get(
    '/{competency_group_id}',
    responses={
        200: {'description': 'Competency group successfully received'},
        404: {'description': 'Competency group not found'}
    },
    summary='Return the competency group'
)
def get_competency_group(competency_group_id: Annotated[int, Path(gt=0)], session: SessionDep) -> CompetencyGroupRead:
    """Return the competency group with the specified id"""
    competency_group = session.get(CompetencyGroup, competency_group_id)
    if not competency_group:
        raise CompetencyGroupNotFoundException()
    return competency_group


@router.patch(
    '/{competency_group_id}',
    responses={
        200: {'description': 'Competency group successfully updated'},
        404: {'description': 'Competency group not found'},
        409: {'description': 'Competency group data is not unique'}
    },
    summary='Update the competency group'
)
def update_competency_group(
    competency_group_id: Annotated[int, Path(gt=0)],
    competency_group_data: CompetencyGroupUpdate,
    session: SessionDep
) -> CompetencyGroupRead:
    """Update the competency group with the specified id with the given information (blank values are ignored)"""
    competency_group = session.get(CompetencyGroup, competency_group_id)
    if not competency_group:
        raise CompetencyGroupNotFoundException()

    if competency_group_data.name:
        stmt = select(exists().where(and_(
            CompetencyGroup.name == competency_group_data.name, CompetencyGroup.id != competency_group_id)
        ))
        if session.execute(stmt).scalar():
            raise CompetencyGroupNameIsNotUniqueException()

    for key, value in competency_group_data.model_dump(exclude_none=True).items():
        setattr(competency_group, key, value)
    session.commit()
    session.refresh(competency_group)
    return competency_group


@router.delete(
    '/{competency_group_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Competency group successfully deleted'},
        404: {'description': 'Competency group not found'},
    },
    summary='Delete the competency group'
)
def delete_competency_group(competency_group_id: Annotated[int, Path(gt=0)], session: SessionDep) -> Response:
    """Delete the competency group with the specified id."""
    competency_group = session.get(CompetencyGroup, competency_group_id)
    if not competency_group:
        raise CompetencyGroupNotFoundException()
    session.delete(competency_group)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    '',
    responses={200: {'description': 'Competency groups successfully received'}},
    summary='Return a list of competency groups'
)
def get_competency_groups(session: SessionDep) -> list[CompetencyGroupRead]:
    """Return a list of competency groups."""
    competency_groups = session.execute(select(CompetencyGroup)).scalars()
    return competency_groups


@router.post(
    '',
    response_model=CompetencyGroupRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'Competency group successfully created'},
        409: {'description': 'Competency group data is not unique'}
    },
    summary='Create the competency group'
)
def create_competency_group(competency_group_data: CompetencyGroupCreate, session: SessionDep) -> Any:
    """Create the competency group with the given information."""
    stmt = select(exists().where(CompetencyGroup.name == competency_group_data.name))
    if session.execute(stmt).scalar():
        raise CompetencyGroupNameIsNotUniqueException()

    competency_group = CompetencyGroup(**competency_group_data.model_dump())
    session.add(competency_group)
    session.commit()
    session.refresh(competency_group)
    return competency_group
