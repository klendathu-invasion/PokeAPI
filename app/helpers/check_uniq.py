from pydantic import BaseModel


class CheckUniqHelper(BaseModel):
    equal_list: list[str] = []
    ilike_list: list[str] = []
    name: str
