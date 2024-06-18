from pydantic import BaseModel, field_validator, model_validator


class CustomBase(BaseModel):
    # Prevent crash from empty value in BDD instead None value.
    @field_validator("*", mode="before")
    @classmethod
    def check_empty_value(cls, v):
        if v == "":
            return None
        return v


class HeritableCustomBase(CustomBase):
    # add successor predecessor logic in schema
    predecessor_id: int | None = None
    successors: str | list = []
    predecessor: str | None = None

    @classmethod
    @model_validator(mode="before")
    def set__type(cls, values):
        values["successors"] = f"list[{cls.__name__}]"
        values["predecessor"] = cls.__name__
        return values
