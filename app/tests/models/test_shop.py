from sqlalchemy.orm.decl_api import DeclarativeMeta

from ... import models
from ..test_main import session
from .model_test import ModelTest


class TestShop(ModelTest):
    class_name: str = "shop"
    fake_model: str = "fake_shop"
    class_model: DeclarativeMeta = models.shop.Shop
    default_columns: dict = {
        "name": "str",
        "user": "model",
    }
    like_test: str = "name"
    relations: list[str] = ["user"]
    option_relation_test: str = "products"
