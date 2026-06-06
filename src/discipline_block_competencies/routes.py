from typing import Annotated, Any

from fastapi import APIRouter, Path, status
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import and_, exists, select

from src.competencies.model import Competency
from src.dependencies import SessionDep
from src.discipline_blocks.model import DisciplineBlock

from .model import DisciplineBlockCompetency

router = APIRouter(
    prefix='/discipline-block-competencies',
    tags=['discipline block competencies'],
)


class DisciplineBlockCompetencyCreate(BaseModel):
    discipline_block_id: Annotated[int, Field(gt=0)]
    competency_id: Annotated[int, Field(gt=0)]


class DisciplineBlockCompetencyUpdate(BaseModel):
    discipline_block_id: Annotated[int | None, Field(gt=0)] = None
    competency_id: Annotated[int | None, Field(gt=0)] = None


class DisciplineBlockCompetencyRead(DisciplineBlockCompetencyCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


@router.get(
    '',
    response_model=list[DisciplineBlockCompetencyRead],
    responses={200: {'description': 'Relations successfully received'}},
    summary='Return a list of discipline block competencies',
)
def get_all(session: SessionDep) -> list[DisciplineBlockCompetencyRead]:
    return session.execute(
        select(DisciplineBlockCompetency).order_by(DisciplineBlockCompetency.id)
    ).scalars().all()


@router.get(
    '/{link_id}',
    response_model=DisciplineBlockCompetencyRead,
    responses={200: {'description': 'Relation successfully received'}, 404: {'description': 'Relation not found'}},
    summary='Return the relation',
)
def get_by_id(link_id: Annotated[int, Path(gt=0)], session: SessionDep) -> DisciplineBlockCompetencyRead:
    link = session.get(DisciplineBlockCompetency, link_id)
    if not link:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail='Связь не найдена')
    return link


@router.post(
    '',
    response_model=DisciplineBlockCompetencyRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'Relation successfully created'},
        404: {'description': 'Discipline block or competency not found'},
        409: {'description': 'Relation already exists'},
    },
    summary='Create the relation',
)
def create_relation(data: DisciplineBlockCompetencyCreate, session: SessionDep) -> Any:
    if not session.get(DisciplineBlock, data.discipline_block_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail='Блок дисциплины не найден')

    if not session.get(Competency, data.competency_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail='Компетенция не найдена')

    stmt = select(
        exists().where(
            and_(
                DisciplineBlockCompetency.discipline_block_id == data.discipline_block_id,
                DisciplineBlockCompetency.competency_id == data.competency_id,
            )
        )
    )
    if session.execute(stmt).scalar():
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail='Такая связь уже существует')

    link = DisciplineBlockCompetency(**data.model_dump())
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


@router.delete(
    '/{link_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={204: {'description': 'Relation successfully deleted'}, 404: {'description': 'Relation not found'}},
    summary='Delete the relation',
)
def delete_relation(link_id: Annotated[int, Path(gt=0)], session: SessionDep) -> Response:
    link = session.get(DisciplineBlockCompetency, link_id)
    if not link:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail='Связь не найдена')

    session.delete(link)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)