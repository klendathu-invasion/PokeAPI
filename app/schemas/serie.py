from datetime import date, datetime
from typing import Annotated

from pydantic import (
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
    validator,
)

from .custom_base import CustomBase


class SerieBase(CustomBase):
    name: Annotated[str, StringConstraints()] = Field(
        examples=["Ecarlate et violet"], description="Le nom du Serie"
    )
    tag: Annotated[str, StringConstraints()] = Field(
        examples=["ev"], description="Le tag du Serie"
    )
    logo: Annotated[str, StringConstraints()] = Field(
        examples=["img url"], description="l'url du logo du Serie"
    )


class Serie(SerieBase):
    id: int
    updated_at: datetime
    created_at: datetime
    symbol_tag: str

    first_edition_count: int | None = 0
    holo_count: int | None = 0
    normal_count: int | None = 0
    official_count: int | None = 0
    reverse_count: int | None = 0
    total_count: int | None = 0

    expanded: bool
    standard: bool

    realease: date
    model_config = ConfigDict(from_attributes=True)


class SerieList(Serie):
    pass


class SerieComplete(Serie):
    pass
