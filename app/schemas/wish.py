from typing import Annotated

from pydantic import ConfigDict, StringConstraints, field_validator

from .custom_base import CustomBase
from .user import User


class WishUpdate(CustomBase):
    name: Annotated[
        str | None, StringConstraints(min_length=1, strip_whitespace=True)
    ] = None
    description: Annotated[
        str | None, StringConstraints(min_length=1, strip_whitespace=True)
    ] = None


class WishBase(CustomBase):
    name: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    user_id: int
    description: Annotated[
        str | None, StringConstraints(min_length=1, strip_whitespace=True)
    ] = None


class Wish(WishBase):
    id: int
    user: User
    model_config = ConfigDict(from_attributes=True)


class WishComplete(Wish):
    product_ids: list[int] = []

    @field_validator("product_ids", mode="before")
    @classmethod
    def product_ids_validator(cls, value) -> list[str]:
        return list(value)