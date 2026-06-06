from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

class IndicatorCreate(BaseModel):
    code: Annotated[str, Field(example='УК-1.1', max_length=10)]
    name: Annotated[str, Field(example='Знать методики поиска и обработки информации', max_length=511)]
    competency_id: Annotated[int, Field(gt=0, example=1)]

class IndicatorUpdate(BaseModel):
    code: Annotated[str | None, Field(example='УК-1.1', max_length=10)] = None
    name: Annotated[str | None, Field(example='Знать методики поиска и обработки информации', max_length=511)] = None
    competency_id: Annotated[int | None, Field(gt=0, example=1)] = None

class IndicatorRead(IndicatorCreate):
    id: Annotated[int, Field(example=1)]
    model_config = ConfigDict(from_attributes=True)