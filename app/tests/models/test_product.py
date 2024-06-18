from sqlalchemy.orm.decl_api import DeclarativeMeta

from ... import models
from ..test_main import session
from .model_test import ModelTest


class TestProduct(ModelTest):
    class_name: str = "product"
    fake_model: str = "fake_product"
    class_model: DeclarativeMeta = models.product.Product
    default_columns: dict = {
        "name": "str",
        "price": "float",
        "shop": "model",
    }
    like_test: str = "name"
    relations: list[str] = ["shop"]
    # option_relation_test: str = "routers"
