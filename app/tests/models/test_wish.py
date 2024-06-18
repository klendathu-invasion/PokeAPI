from sqlalchemy.orm.decl_api import DeclarativeMeta

from ... import models
from ..test_main import session
from .model_test import ModelTest


class TestWish(ModelTest):
    class_name: str = "wish"
    fake_model: str = "fake_wish"
    class_model: DeclarativeMeta = models.wish.Wish
    default_columns: dict = {
        "name": "str",
        "user": "model",
    }
    like_test: str = "name"
    relations: list[str] = ["user"]
    # option_relation_test: str = "products"
