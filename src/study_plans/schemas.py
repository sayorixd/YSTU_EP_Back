from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StudyPlanCreate(BaseModel):
    educational_plan_id: int
    name: Optional[str] = None
    data: dict


class StudyPlanUpdate(BaseModel):
    name: Optional[str] = None
    data: dict


class StudyPlanOut(BaseModel):
    id: int
    educational_plan_id: int
    name: Optional[str]
    data: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True