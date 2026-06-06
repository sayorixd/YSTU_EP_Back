from typing import Annotated
from pydantic import BaseModel, Field


class EducationalFormCreate(BaseModel):
    name: Annotated[str, Field(example='Очная', max_length=63)]


class EducationalFormUpdate(BaseModel):
    name: Annotated[str | None, Field(example='Очная', max_length=63)] = None


class EducationalFormRead(EducationalFormCreate):
    id: Annotated[int, Field(example=1)]