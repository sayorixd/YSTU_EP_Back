from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict


class DisciplineBlockCreate(BaseModel):
    discipline_id: Annotated[int, Field(example=1)]
    credit_units: Annotated[int, Field(example=3)]
    control_type_ids: Annotated[list[int], Field(example=[1, 2])]
    lecture_hours: Annotated[int, Field(example=40)]
    practice_hours: Annotated[int, Field(example=40)]
    lab_hours: Annotated[int, Field(example=40)]
    semester_number: Annotated[int, Field(example=3)]
    map_core_id: Annotated[int, Field(example=1)]
    has_course_work: Annotated[bool, Field(example=False)]


class DisciplineBlockUpdate(BaseModel):
    discipline_id: Annotated[int | None, Field(example=1)] = None
    credit_units: Annotated[int | None, Field(example=3)] = None
    control_type_ids: Annotated[list[int] | None, Field(example=[1, 2])] = None
    lecture_hours: Annotated[int | None, Field(example=40)] = None
    practice_hours: Annotated[int | None, Field(example=40)] = None
    lab_hours: Annotated[int | None, Field(example=40)] = None
    semester_number: Annotated[int | None, Field(example=3)] = None
    map_core_id: Annotated[int | None, Field(example=1)] = None
    has_course_work: Annotated[bool | None, Field(example=False)] = None


class DisciplineBlockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    discipline_id: int
    credit_units: int
    control_type_ids: list[int]
    lecture_hours: int
    practice_hours: int
    lab_hours: int
    semester_number: int
    map_core_id: int
    has_course_work: bool

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        data = {
            "id": obj.id,
            "discipline_id": obj.discipline_id,
            "credit_units": obj.credit_units,
            "control_type_ids": [
                item.control_type_id
                for item in obj.control_types
            ],
            "lecture_hours": obj.lecture_hours,
            "practice_hours": obj.practice_hours,
            "lab_hours": obj.lab_hours,
            "semester_number": obj.semester_number,
            "map_core_id": obj.map_core_id,
            "has_course_work": obj.has_course_work
        }

        return super().model_validate(
            data,
            *args,
            **kwargs
        )