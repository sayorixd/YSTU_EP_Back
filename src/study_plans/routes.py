from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from src.dependencies import get_db

from . import repository as repo
from . import schemas
from .service import generate_study_plan

router = APIRouter(
    prefix="/study-plans",
    tags=["study plans"]
)


@router.get(
    "",
    response_model=list[
        schemas.StudyPlanOut
    ]
)
def list_study_plans(
        limit: int = 100,
        offset: int = 0,
        db: Session = Depends(get_db)
):
    return repo.list_all(
        db,
        limit=limit,
        offset=offset
    )


@router.get(
    "/{id}",
    response_model=
    schemas.StudyPlanOut
)
def get_study_plan(
        id: int,
        db: Session = Depends(get_db)
):
    obj = repo.get_by_id(db, id)

    if not obj:
        raise HTTPException(
            status_code=404,
            detail="Study plan not found"
        )

    return obj


@router.post(
    "",
    response_model=
    schemas.StudyPlanOut
)
def create_study_plan(
        payload:
        schemas.StudyPlanCreate,
        db: Session = Depends(get_db)
):
    data = {
        "educational_plan_id":
            payload.educational_plan_id,

        "name":
            payload.name,

        "data":
            payload.data
    }

    return repo.create(
        db,
        data
    )


@router.put(
    "/{id}",
    response_model=
    schemas.StudyPlanOut
)
def update_study_plan(
        id: int,
        payload:
        schemas.StudyPlanUpdate,
        db: Session = Depends(get_db)
):
    obj = repo.get_by_id(db, id)

    if not obj:
        raise HTTPException(
            status_code=404,
            detail="Study plan not found"
        )

    return repo.update(
        db,
        obj,
        {
            "name":
                payload.name,

            "data":
                payload.data
        }
    )


@router.delete(
    "/{id}"
)
def delete_study_plan(
        id: int,
        db: Session = Depends(get_db)
):
    obj = repo.get_by_id(
        db,
        id
    )

    if not obj:
        raise HTTPException(
            status_code=404,
            detail="Study plan not found"
        )

    repo.delete(
        db,
        obj
    )

    return {
        "ok": True
    }


@router.get(
    "/by-educational-plan/"
    "{educational_plan_id}",
    response_model=list[
        schemas.StudyPlanOut
    ]
)
def list_by_educational_plan(
        educational_plan_id: int,
        db: Session = Depends(get_db)
):
    return (
        repo
        .list_by_educational_plan(
            db,
            educational_plan_id
        )
    )