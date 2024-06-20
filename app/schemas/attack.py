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


class AttackBase(CustomBase):
    name: Annotated[str, StringConstraints()] = Field(
        examples=["Ecarlate et violet"], description="Le nom de l'attaque"
    )


class Attack(AttackBase):
    id: int
    updated_at: datetime
    created_at: datetime
    effect: str
    dammage: str | None = None
    costs: list[int] | None = []

    realease: datetime
    model_config = ConfigDict(from_attributes=True)


class AttackList(Attack):
    pass


class AttackComplete(Attack):
    pass
