from datetime import datetime
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


class CardBase(CustomBase):
    name: Annotated[str, StringConstraints()] = Field(
        examples=["Ecarlate et violet"], description="Le nom du Card"
    )
    tag: Annotated[str, StringConstraints()] = Field(
        examples=["ev"], description="Le tag du Card"
    )


class Card(CardBase):
    id: int
    updated_at: datetime
    created_at: datetime
    category: str
    local_tag: str
    description: str
    regulation_mark: str
    illustrator: str | None = None
    suffix: str | None = None
    evolve_from: str | None = None

    rarity: int | None = None
    stage: int | None = None
    hp: int | None = None
    level: int | None = None
    retreat: int | None = None

    # should be array
    energy_types: list[int] | None = []
    pokedex_numbers: list[int] | None = []

    expanded: bool
    standard: bool

    realease: datetime
    model_config = ConfigDict(from_attributes=True)


class CardList(Card):
    pass


class CardComplete(Card):
    pass
