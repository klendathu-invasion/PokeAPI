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


class UserBase(CustomBase):
    first_name: Annotated[
        str,
        StringConstraints(
            min_length=2,
            pattern=r"^[a-zA-ZÀ-ÿ]+([ '-]{1}[a-zA-ZÀ-ÿ]+)*$",
            strip_whitespace=True,
        ),
    ] = Field(
        examples=["Prénom"],
        description="The firstname of the user. The firstnam will be titlelize in the database.",
    )
    last_name: Annotated[
        str,
        StringConstraints(
            min_length=2,
            pattern=r"^[a-zA-ZÀ-ÿ]+([ '-]{1}[a-zA-ZÀ-ÿ]+)*$",
            strip_whitespace=True,
            to_upper=True,
        ),
    ] = Field(
        examples=["Nom d'Famille"],
        description="The lastname of the user. Turn all characters in uppercase in the database.",
    )
    email: Annotated[
        EmailStr,
        StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
    ] = Field(
        examples=["prenom.nom@gmail.com"],
        description="The email of the user.",
    )


class User(UserBase):
    id: int
    updated_at: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserComplete(User):
    pass
