from typing import Annotated
from pydantic import BaseModel, Field


class DirectionCreate(BaseModel):
    name: Annotated[str, Field(example='Программная инженерия', max_length=50)]
    educational_level_id: Annotated[int, Field(example=1)]
    educational_form_id: Annotated[int, Field(example=1)]
    semester_count: Annotated[int, Field(ge=1, le=12, example=8)]


class DirectionUpdate(BaseModel):
    name: Annotated[str | None, Field(example='Программная инженерия', max_length=50)]
    educational_level_id: Annotated[int | None, Field(example=1)]
    educational_form_id: Annotated[int | None, Field(example=1)]
    semester_count: Annotated[int | None, Field(ge=1, le=12, example=8)]


class DirectionRead(DirectionCreate):
    id: Annotated[int, Field(example=1)]
