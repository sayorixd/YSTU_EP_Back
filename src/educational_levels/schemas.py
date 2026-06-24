from typing import Annotated
from pydantic import BaseModel, Field


class EducationalLevelCreate(BaseModel):
    name: Annotated[str, Field(example='Бакалавриат', max_length=20)]
    name_in_genetive: Annotated[str, Field(example='Бакалавриата', max_length=255)]


class EducationalLevelUpdate(BaseModel):
    name: Annotated[str | None, Field(example='Бакалавриат', max_length=20)]
    name_in_genetive: Annotated[str | None, Field(example='Бакалавриата', max_length=255)]


class EducationalLevelRead(EducationalLevelCreate):
    id: Annotated[int, Field(example=1)]
