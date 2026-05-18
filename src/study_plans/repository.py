from sqlalchemy.orm import Session

from .model import StudyPlan


def get_by_id(db: Session, id: int):
    return (
        db.query(StudyPlan)
        .filter(StudyPlan.id == id)
        .first()
    )


def list_all(
        db: Session,
        limit: int = 100,
        offset: int = 0
):
    return (
        db.query(StudyPlan)
        .order_by(StudyPlan.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def create(db: Session, obj_in: dict):
    obj = StudyPlan(**obj_in)

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


def update(
        db: Session,
        db_obj,
        obj_in: dict
):
    for k, v in obj_in.items():
        setattr(db_obj, k, v)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    return db_obj


def delete(db: Session, db_obj):
    db.delete(db_obj)
    db.commit()

    return True


def list_by_educational_plan(
        db: Session,
        educational_plan_id: int
):
    return (
        db.query(StudyPlan)
        .filter(
            StudyPlan.educational_plan_id
            == educational_plan_id
        )
        .all()
    )