from fastapi import APIRouter, status, Path
from fastapi.responses import Response
from sqlalchemy import select
from typing import Annotated, Any
from src.dependencies import SessionDep
from src.exceptions import (
    DisciplineBlockNotFoundException, DisciplineNotFoundException, ControlTypeNotFoundException,
    MapCoreNotFoundException
)
from src.control_types.model import ControlType
from src.disciplines.model import Discipline
from .model import DisciplineBlock
from src.map_cors.model import MapCore
from .schemas import DisciplineBlockCreate, DisciplineBlockUpdate, DisciplineBlockRead

router = APIRouter(
    prefix='/discipline-blocks',
    tags=['discipline blocks']
)


@router.get(
    '/{discipline_block_id}',
    responses={
        200: {'description': 'Discipline block successfully received'},
        404: {'description': 'Discipline block not found'}
    },
    summary='Return the discipline block'
)
def get_discipline_block(discipline_block_id: Annotated[int, Path(gt=0)], session: SessionDep) -> DisciplineBlockRead:
    """Return the discipline block with the specified id"""
    discipline_block = session.get(DisciplineBlock, discipline_block_id)
    if not discipline_block:
        raise DisciplineBlockNotFoundException()


    return {
        "id": discipline_block.id,
        "discipline_id": discipline_block.discipline_id,
        "credit_units": discipline_block.credit_units,
        "control_type_id": discipline_block.control_type_id,
        "lecture_hours": discipline_block.lecture_hours,
        "practice_hours": discipline_block.practice_hours,
        "lab_hours": discipline_block.lab_hours,
        "semester_number":
            discipline_block.semester_number,
        "map_core_id":
            discipline_block.map_core_id,
        "has_course_project":
            discipline_block.has_course_project,
        "has_course_work":
            discipline_block.has_course_work,
        "has_rz":
            discipline_block.has_rz,
        "has_gr":
            discipline_block.has_rgr,
        "has_referat":
            discipline_block.has_referat
    }


@router.patch(
    '/{discipline_block_id}',
    responses={
        200: {'description': 'Discipline block successfully updated'},
        404: {'description': 'Discipline block, discipline, control type or map core not found'}
    },
    summary='Update the discipline block'
)
def update_discipline_block(
        discipline_block_id: Annotated[int, Path(gt=0)],
        discipline_block_data: DisciplineBlockUpdate,
        session: SessionDep
) -> DisciplineBlockRead:
    """Update the discipline block with the specified id with the given information (blank values are ignored)"""
    discipline_block = session.get(DisciplineBlock, discipline_block_id)
    if not discipline_block:
        raise DisciplineBlockNotFoundException()

    if discipline_block_data.discipline_id:
        if not session.get(Discipline, discipline_block_data.discipline_id):
            raise DisciplineNotFoundException()

    if discipline_block_data.control_type_id:
        if not session.get(
                ControlType,
                discipline_block_data.control_type_id
        ):
            raise ControlTypeNotFoundException()

    if discipline_block_data.map_core_id:
        if not session.get(MapCore, discipline_block_data.map_core_id):
            raise MapCoreNotFoundException()

    update_data = discipline_block_data.model_dump(
        exclude_none=True
    )

    for key, value in update_data.items():
        setattr(discipline_block, key, value)

    if discipline_block_data.control_type_id is not None:
        discipline_block.control_type_id = (
            discipline_block_data.control_type_id
        )

    session.commit()
    session.refresh(discipline_block)

    return DisciplineBlockRead(
        id=discipline_block.id,
        discipline_id=discipline_block.discipline_id,
        credit_units=discipline_block.credit_units,
        control_type_id=discipline_block.control_type_id,
        lecture_hours=discipline_block.lecture_hours,
        practice_hours=discipline_block.practice_hours,
        lab_hours=discipline_block.lab_hours,
        semester_number=discipline_block.semester_number,
        map_core_id=discipline_block.map_core_id,
        has_course_project=discipline_block.has_course_project,
        has_course_work=discipline_block.has_course_work,
        has_rz=discipline_block.has_rz,
        has_rgr=discipline_block.has_rgr,
        has_referat=discipline_block.has_referat,
    )


@router.delete(
    '/{discipline_block_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Discipline block successfully deleted'},
        404: {'description': 'Discipline block not found'},
    },
    summary='Delete the discipline block'
)
def delete_discipline_block(discipline_block_id: Annotated[int, Path(gt=0)], session: SessionDep) -> Response:
    """Delete the discipline block with the specified id."""
    discipline_block = session.get(DisciplineBlock, discipline_block_id)
    if not discipline_block:
        raise DisciplineBlockNotFoundException()
    session.delete(discipline_block)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    '',
    responses={200: {'description': 'Discipline blocks successfully received'}},
    summary='Return a list of discipline blocks'
)
def get_discipline_blocks(session: SessionDep) -> list[DisciplineBlockRead]:
    """Return a list of discipline blocks."""
    discipline_blocks = session.execute(
        select(DisciplineBlock)
    ).scalars().all()

    result = []

    for discipline_block in discipline_blocks:

        result.append({
            "id": discipline_block.id,
            "discipline_id":
                discipline_block.discipline_id,
            "credit_units":
                discipline_block.credit_units,
            "control_type_id":
                discipline_block.control_type_id,
            "lecture_hours":
                discipline_block.lecture_hours,
            "practice_hours":
                discipline_block.practice_hours,
            "lab_hours":
                discipline_block.lab_hours,
            "semester_number":
                discipline_block.semester_number,
            "map_core_id":
                discipline_block.map_core_id,
            "has_course_project":
                discipline_block.has_course_project,
            "has_course_work":
                discipline_block.has_course_work,
            "has_rz":
                discipline_block.has_rz,
            "has_rgr":
                discipline_block.has_rgr,
            "has_referat":
                discipline_block.has_referat,
        })

    return result


@router.post(
    '',
    response_model=DisciplineBlockRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'Discipline block successfully created'},
        404: {'description': 'Discipline, control type or map core not found'},
    },
    summary='Create the discipline block'
)
def create_discipline_block(
        discipline_block_data: DisciplineBlockCreate,
        session: SessionDep
) -> DisciplineBlockRead:
    """Create the discipline block with the given information."""

    if not session.get(
            Discipline,
            discipline_block_data.discipline_id
    ):
        raise DisciplineNotFoundException()

    if not session.get(
            ControlType,
            discipline_block_data.control_type_id
    ):
        raise ControlTypeNotFoundException()

    if not session.get(
            MapCore,
            discipline_block_data.map_core_id
    ):
        raise MapCoreNotFoundException()

    discipline_block_data_dict = (
        discipline_block_data.model_dump()
    )

    discipline_block = DisciplineBlock(
        **discipline_block_data.model_dump()
    )

    session.add(discipline_block)
    session.commit()
    session.refresh(discipline_block)

    session.commit()

    return DisciplineBlockRead(
        id=discipline_block.id,
        discipline_id=discipline_block.discipline_id,
        credit_units=discipline_block.credit_units,
        control_type_id=discipline_block.control_type_id,
        lecture_hours=discipline_block.lecture_hours,
        practice_hours=discipline_block.practice_hours,
        lab_hours=discipline_block.lab_hours,
        semester_number=discipline_block.semester_number,
        map_core_id=discipline_block.map_core_id,
        has_course_project=discipline_block.has_course_project,
        has_course_work=discipline_block.has_course_work,
        has_rz=discipline_block.has_rz,
        has_rgr=discipline_block.has_rgr,
        has_referat=discipline_block.has_referat,
    )