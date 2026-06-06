from typing import Annotated, Any

from fastapi import APIRouter, Path, status
from fastapi.responses import Response
from sqlalchemy import and_, exists, select

from src.competencies.model import Competency
from src.dependencies import SessionDep
from src.exceptions import (
    CompetencyNotFoundException,
    IndicatorCodeIsNotUniqueException,
    IndicatorNotFoundException,
)

from .model import Indicator
from .schemas import IndicatorCreate, IndicatorRead, IndicatorUpdate

router = APIRouter(
    prefix='/indicators',
    tags=['indicators'],
)


@router.get(
    '/{indicator_id}',
    responses={
        200: {'description': 'Indicator successfully received'},
        404: {'description': 'Indicator not found'},
    },
    summary='Return the indicator',
)
def get_indicator(indicator_id: Annotated[int, Path(gt=0)], session: SessionDep) -> IndicatorRead:
    indicator = session.get(Indicator, indicator_id)
    if not indicator:
        raise IndicatorNotFoundException()
    return indicator


@router.patch(
    '/{indicator_id}',
    responses={
        200: {'description': 'Indicator successfully updated'},
        404: {'description': 'Indicator or competency not found'},
        409: {'description': 'Indicator data is not unique'},
    },
    summary='Update the indicator',
)
def update_indicator(
    indicator_id: Annotated[int, Path(gt=0)],
    indicator_data: IndicatorUpdate,
    session: SessionDep,
) -> IndicatorRead:
    indicator = session.get(Indicator, indicator_id)
    if not indicator:
        raise IndicatorNotFoundException()

    if indicator_data.code is not None:
        stmt = select(
            exists().where(
                and_(
                    Indicator.code == indicator_data.code,
                    Indicator.id != indicator_id,
                )
            )
        )
        if session.execute(stmt).scalar():
            raise IndicatorCodeIsNotUniqueException()

    if indicator_data.competency_id is not None:
        competency = session.get(Competency, indicator_data.competency_id)
        if not competency:
            raise CompetencyNotFoundException()

    for key, value in indicator_data.model_dump(exclude_none=True).items():
        setattr(indicator, key, value)

    session.commit()
    session.refresh(indicator)
    return indicator


@router.delete(
    '/{indicator_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Indicator successfully deleted'},
        404: {'description': 'Indicator not found'},
    },
    summary='Delete the indicator',
)
def delete_indicator(indicator_id: Annotated[int, Path(gt=0)], session: SessionDep) -> Response:
    indicator = session.get(Indicator, indicator_id)
    if not indicator:
        raise IndicatorNotFoundException()
    session.delete(indicator)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    '',
    response_model=list[IndicatorRead],
    responses={200: {'description': 'Indicators successfully received'}},
    summary='Return a list of indicators',
)
def get_indicators(session: SessionDep) -> list[IndicatorRead]:
    return session.execute(select(Indicator).order_by(Indicator.id)).scalars().all()


@router.post(
    '',
    response_model=IndicatorRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'Indicator successfully created'},
        404: {'description': 'Competency not found'},
        409: {'description': 'Indicator data is not unique'},
    },
    summary='Create the indicator',
)
def create_indicator(indicator_data: IndicatorCreate, session: SessionDep) -> Any:
    stmt = select(exists().where(Indicator.code == indicator_data.code))
    if session.execute(stmt).scalar():
        raise IndicatorCodeIsNotUniqueException()

    competency = session.get(Competency, indicator_data.competency_id)
    if not competency:
        raise CompetencyNotFoundException()

    indicator = Indicator(**indicator_data.model_dump())
    session.add(indicator)
    session.commit()
    session.refresh(indicator)
    return indicator