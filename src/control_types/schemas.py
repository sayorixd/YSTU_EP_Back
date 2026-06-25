from typing import Annotated
from pydantic import BaseModel, Field

class ControlTypeCreate(BaseModel):
    name: Annotated[str, Field(example='Дифференцированный зачет', max_length=30)]
    is_primary: Annotated[bool, Field(example=False)] = False

class ControlTypeUpdate(BaseModel):
    name: Annotated[str | None, Field(example='Дифференцированный зачет', max_length=30)] = None
    is_primary: Annotated[bool | None, Field(example=False)] = None

class ControlTypeRead(ControlTypeCreate):
    id: Annotated[int, Field(example=1)]