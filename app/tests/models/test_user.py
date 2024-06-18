from sqlalchemy.orm.decl_api import DeclarativeMeta

from ... import models
from ..test_main import session
from .model_test import ModelTest


class TestUser(ModelTest):
    class_name: str = "user"
    fake_model: str = "fake_user"
    class_model: DeclarativeMeta = models.user.User
    default_columns: dict = {
        "matricule": "str",
        "first_name": "name",
        "last_name": "name",
        "email": "str",
    }
    like_test: str = "email"
    # option_relation_test: str = "alerts"
