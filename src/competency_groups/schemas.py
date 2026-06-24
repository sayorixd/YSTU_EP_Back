from typing import Annotated
from pydantic import BaseModel, Field


class CompetencyGroupCreate(BaseModel):
    name: Annotated[str, Field(example='Общекультурные компетенции', max_length=255)]
    short_name: Annotated[str, Field(example='ОК', max_length=255)]


class CompetencyGroupUpdate(BaseModel):
    name: Annotated[str | None, Field(example='Общекультурные компетенции', max_length=255)]
    short_name: Annotated[str | None, Field(example='ОК', max_length=255)]


class CompetencyGroupRead(CompetencyGroupCreate):
    id: Annotated[int, Field(example=1)]
