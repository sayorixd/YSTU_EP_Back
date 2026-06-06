from typing import Annotated
from pydantic import BaseModel, Field, field_validator, ConfigDict


def _normalize_indicators(values: list[str]) -> list[str]:
    cleaned = [v.strip() for v in values if isinstance(v, str)]
    if not 1 <= len(cleaned) <= 10:
        raise ValueError('Количество индикаторов должно быть от 1 до 10')
    if any(not v for v in cleaned):
        raise ValueError('Все индикаторы должны быть заполнены')
    return cleaned


class IndicatorBase(BaseModel):
    competency_id: Annotated[int, Field(gt=0, example=1)]
    group_name: Annotated[str, Field(max_length=255, example='Группа индикаторов 1')]
    indicators: Annotated[list[str], Field(min_length=1, max_length=10)]

    @field_validator('indicators')
    @classmethod
    def validate_indicators(cls, value: list[str]) -> list[str]:
        return _normalize_indicators(value)


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorUpdate(BaseModel):
    competency_id: Annotated[int | None, Field(gt=0, example=1)] = None
    group_name: Annotated[str | None, Field(max_length=255, example='Группа индикаторов 1')] = None
    indicators: Annotated[list[str] | None, Field(min_length=1, max_length=10)] = None

    @field_validator('indicators')
    @classmethod
    def validate_indicators(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return _normalize_indicators(value)


class IndicatorRead(IndicatorBase):
    id: Annotated[int, Field(example=1)]

    model_config = ConfigDict(from_attributes=True)