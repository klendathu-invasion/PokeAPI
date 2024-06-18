from sqlalchemy.orm.decl_api import DeclarativeMeta

from ... import models
from ..test_main import session
from .model_test import ModelTest


class TestCart(ModelTest):
    class_name: str = "cart"
    fake_model: str = "fake_cart"
    class_model: DeclarativeMeta = models.cart.Cart
    default_columns: dict = {
        "quantity": "int",
        "product": "model",
        "user": "model",
    }
    # like_test: str = "name"
    relations: list[str] = ["product", "user"]
    # option_relation_test: str = "routers"
