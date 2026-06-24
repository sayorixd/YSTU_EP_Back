from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

class DisciplineBlockCreate(BaseModel):
    discipline_id: int
    credit_units: int
    control_type_id: int
    lecture_hours: int
    practice_hours: int
    lab_hours: int
    semester_number: int
    map_core_id: int
    secondary_control_type_ids: list[int] = []

class DisciplineBlockUpdate(BaseModel):
    discipline_id: int | None = None
    credit_units: int | None = None
    control_type_id: int | None = None
    lecture_hours: int | None = None
    practice_hours: int | None = None
    lab_hours: int | None = None
    semester_number: int | None = None
    map_core_id: int | None = None
    secondary_control_type_ids: list[int] | None = None

class DisciplineBlockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    discipline_id: int
    credit_units: int
    control_type_id: int
    lecture_hours: int
    practice_hours: int
    lab_hours: int
    semester_number: int
    map_core_id: int
    secondary_control_type_ids: list[int] = []