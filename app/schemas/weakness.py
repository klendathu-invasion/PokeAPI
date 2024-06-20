from datetime import date, datetime

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


class WeaknessBase(CustomBase):
    pass


class Weakness(WeaknessBase):
    id: int
    updated_at: datetime
    created_at: datetime
    value: str

    energy_type: int | None = 0

    realease: date
    model_config = ConfigDict(from_attributes=True)


class WeaknessList(Weakness):
    pass


class WeaknessComplete(Weakness):
    pass
