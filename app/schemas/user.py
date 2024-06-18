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
    matricule: Annotated[
        str, StringConstraints(min_length=1, strip_whitespace=True)
    ] = Field(examples=["matricule_company"])
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
    is_pro: bool = False

    @field_validator("first_name", mode="before")
    @classmethod
    def first_name_transform(cls, value: str) -> str:
        return value.title()


class User(UserBase):
    id: int
    legals_version: str | None = None
    legals_at: datetime | None = None
    last_connection_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class UserComplete(User):
    admin: list = []
    shop_ids: list[int] = []
    is_admin: bool = Field(
        default=False,
        examples=[False],
        description="The flag to know if user is admin or not.",
    )

    @validator(
        "shop_ids",
        pre=True,
    )
    def ids_validator(cls, value) -> list[str]:
        return list(value)

    @model_validator(mode="after")
    @classmethod
    def populate_is_admin(cls, user):
        user.is_admin = len(user.admin) > 0
        return user
