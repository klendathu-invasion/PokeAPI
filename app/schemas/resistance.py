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


class ResistanceBase(CustomBase):
    pass


class Resistance(ResistanceBase):
    id: int
    updated_at: datetime
    created_at: datetime
    value: str

    energy_type: int | None = 0

    realease: date
    model_config = ConfigDict(from_attributes=True)


class ResistanceList(Resistance):
    pass


class ResistanceComplete(Resistance):
    pass
