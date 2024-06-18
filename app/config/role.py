from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models, schemas
from ..utils.tools import Tools


class Role(BaseModel):
    __tables_by_id__ = {
        "cart_id": {
            "class": "cart",
            "parent": ["user"],
            "parent_id": "user_id",
            "table": "carts",
            "role": "possessor",
        },
        "product_id": {
            "class": "product",
            "parent": ["shop"],
            "parent_id": "shop_id",
            "table": "products",
            "role": "owner",
        },
        "shop_id": {
            "class": "shop",
            "parent": ["user"],
            "parent_id": "user_id",
            "table": "shops",
            "role": "owner",
        },
        "wish_id": {
            "class": "wish",
            "parent": ["user"],
            "parent_id": "user_id",
            "table": "wishes",
            "role": "possessor",
        },
        "user_id": {"class": "user", "table": "users"},
    }

    __roles__ = ["admin", "owner", "member", "pro", "possessor", "client"]
