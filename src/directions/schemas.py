from typing import Annotated
from pydantic import BaseModel, Field


class DirectionCreate(BaseModel):
    name: Annotated[str, Field(example='09.03.04 Программная инженерия 2026-2027', max_length=50)]
    code: Annotated[str, Field(example='09.03.04', max_length=255)]
    profile: Annotated[str, Field(example='Программная инженерия', max_length=255)]
    educational_level_id: Annotated[int, Field(example=1)]
    educational_form_id: Annotated[int, Field(example=1)]
    semester_count: Annotated[int, Field(ge=1, le=12, example=8)]


class DirectionUpdate(BaseModel):
    name: Annotated[str, Field(example='09.03.04 Программная инженерия 2026-2027', max_length=50)]
    code: Annotated[str, Field(example='09.03.04', max_length=255)]
    profile: Annotated[str, Field(example='Программная инженерия', max_length=255)]
    educational_level_id: Annotated[int | None, Field(example=1)]
    educational_form_id: Annotated[int | None, Field(example=1)]
    semester_count: Annotated[int | None, Field(ge=1, le=12, example=8)]


class DirectionRead(DirectionCreate):
    id: Annotated[int, Field(example=1)]
