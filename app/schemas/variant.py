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


class VariantBase(CustomBase):
    name: Annotated[str, StringConstraints()] = Field(
        examples=["Ecarlate et violet"], description="Le nom du Variant"
    )
    tag: Annotated[str, StringConstraints()] = Field(
        examples=["ev"], description="Le tag du Variant"
    )


class Variant(VariantBase):
    id: int
    updated_at: datetime
    created_at: datetime
    description: str
    url_image: str

    realease: datetime
    model_config = ConfigDict(from_attributes=True)


class VariantList(Variant):
    pass


class VariantComplete(Variant):
    pass
