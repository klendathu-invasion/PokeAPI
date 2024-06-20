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


class BlockBase(CustomBase):
    name: Annotated[str, StringConstraints()] = Field(
        examples=["Ecarlate et violet"], description="Le nom du block"
    )
    tag: Annotated[str, StringConstraints()] = Field(
        examples=["ev"], description="Le tag du block"
    )
    logo: Annotated[str, StringConstraints()] = Field(
        examples=["img url"], description="l'url du logo du block"
    )


class Block(BlockBase):
    id: int
    updated_at: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BlockList(Block):
    pass


class BlockComplete(Block):
    pass
