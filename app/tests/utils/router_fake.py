import enum
from datetime import datetime

import i18n
import pytest
import pytest_check as check
from fastapi import status
from fastapi.logger import logger
from pydantic import BaseModel

from ... import models, schemas
from ...utils.tools import Tools
from ..test_main import TestClient, TestingSessionLocal, fake
from . import fake_model
from .switch_fake import SwitchFake
from .tools import get_levels


def get_model_attribute_json(model: dict, attribute: str):
    model_attribute = model[attribute]
    if isinstance(model_attribute, datetime):
        model_attribute = model_attribute.isoformat()
    elif isinstance(model_attribute, enum.Enum):
        model_attribute = model_attribute.value
    return model_attribute


class RouterFake(BaseModel):
    attributes: dict
    class_name: str
    fake_method_name: str
    ids_join: list[str] = []
    message_model_name: str
    name: str
    name_model_id: str
    name_model_key: str
    owner: str | None = None
    parents: list[str] = []
    tablename: str
    uniq_attribute: str | None = None
    update_attributes: list[str] = []
    message_already: str = "errors.already_with_name"
    message_invalid_role: str = "errors.invalid_role"
    message_not_found: str = "errors.not_found_with_name"

    def __init__(self, *, name: str, tablename: str, **kwargs):
        super().__init__(
            class_name=f"{name}.{name.title().replace('_', '')}",
            name=name,
            fake_method_name=f"fake_{name}",
            message_model_name=f"models.{tablename}.name",
            name_model_key=f"{name}_json",
            name_model_id=f"{name}_id",
            tablename=tablename,
            **kwargs,
        )

    def list(
        self,
        request,
        session: TestingSessionLocal,
        fake_ability: dict,
        list_attribute: str | None = None,
    ):
        return_json = {
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "list_attribute": (
                "/list" if list_attribute is None else f"/{list_attribute}/0"
            ),
        }
        if fake_ability["response"]:
            if list_attribute is None:
                return_json["status_code"] = status.HTTP_200_OK
                return return_json
            role = fake_ability["role"]
            user = schemas.user.UserComplete.model_validate(fake_ability["user"])
            if request.param == "invalid_manager" and role != "admin":
                return_json["response_json"] = {
                    "detail": i18n.t(self.message_invalid_role)
                }
                return return_json

            model_id = f"{list_attribute}_id"
            levels = get_levels(session, role, user, self.owner)
            param_id = (
                getattr(fake_model, f"fake_{list_attribute}")(session, **levels).id
                if model_id not in levels or levels[model_id] is None
                else levels[model_id]
            )
            print("--------------------------------")
            print(
                f"{list_attribute = } | {param_id = } | {role = } | {levels = } | {user = }"
            )
            return_json["list_attribute"] = f"/{list_attribute}/{param_id}"
            return_json["status_code"] = status.HTTP_200_OK
            return return_json
        return_json["status_code"] = fake_ability["status_code"]
        return_json["response_json"] = fake_ability["message"]
        return return_json

    def create(self, request, session: TestingSessionLocal, fake_ability: dict):
        model_json = {}
        for _attribute, _type in self.attributes.items():
            model_json[_attribute] = SwitchFake.fake(attribute_type=_type)
        return_json = {
            self.name_model_key: model_json,
            "status_code": status.HTTP_401_UNAUTHORIZED,
        }
        if fake_ability["response"]:
            role = fake_ability["role"]
            user = schemas.user.UserComplete.model_validate(fake_ability["user"])
            if request.param == "invalid_manager" and role != "admin":
                return_json["response_json"] = {
                    "detail": i18n.t(self.message_invalid_role)
                }
                return return_json
            levels = get_levels(session, role, user, self.owner)
            for parent in self.parents:
                parent_id = f"{parent}_id"

                return_json[self.name_model_key][parent_id] = (
                    getattr(fake_model, f"fake_{parent}")(session, **levels).id
                    if parent_id not in levels or levels[parent_id] is None
                    else levels[parent_id]
                )
                print("=============================")
                print(f"{return_json[self.name_model_key][parent_id] = }")
                print("=============================")

            if request.param == "already_exist" and self.uniq_attribute is not None:
                model = getattr(fake_model, self.fake_method_name)(
                    session, **levels
                ).as_dict()

                for _attribute in self.attributes:
                    model_attribute = get_model_attribute_json(model, _attribute)
                    return_json[self.name_model_key][_attribute] = model_attribute
                return_json["status_code"] = status.HTTP_400_BAD_REQUEST
                return_json["response_json"] = {
                    "detail": i18n.t(
                        self.message_already,
                        name=i18n.t(f"models.{self.tablename}.{self.uniq_attribute}"),
                    )
                }
                print(f"{model = } | {return_json = }")
                if "user_id" in dir(model):
                    print(f"{model.user_id = } | {levels = }")
                return return_json
            return_json["status_code"] = status.HTTP_201_CREATED
            return return_json
        return_json["status_code"] = fake_ability["status_code"]
        return_json["response_json"] = fake_ability["message"]
        return return_json

    def read(self, request, session: TestingSessionLocal, fake_ability: dict):
        return_json = {
            self.name_model_id: 0,
            "status_code": status.HTTP_401_UNAUTHORIZED,
        }
        if fake_ability["response"]:
            role = fake_ability["role"]
            user = schemas.user.UserComplete.model_validate(fake_ability["user"])
            allowed_roles = ["admin"]
            if self.owner == "pro":
                allowed_roles += ["possessor", "client"]
            if role not in allowed_roles and request.param != "valid_manager":
                return_json["response_json"] = {
                    "detail": i18n.t(self.message_invalid_role)
                }
                return return_json
            elif request.param == "not_found":
                return_json["status_code"] = status.HTTP_404_NOT_FOUND
                return_json["response_json"] = {
                    "detail": i18n.t(
                        self.message_not_found, name=i18n.t(self.message_model_name)
                    )
                }
                return return_json
            levels = get_levels(session, role, user, self.owner)
            model = (
                getattr(fake_model, self.fake_method_name)(session, **levels)
                if self.name_model_id not in levels
                or levels[self.name_model_id] is None
                else Tools.get_class_from_string(models, self.class_name).find_by(
                    session, id=levels[self.name_model_id]
                )
            )
            print(f"{model = }")
            return_json[self.name_model_id] = model.id
            return_json["status_code"] = status.HTTP_200_OK
            print(f"{return_json = }")
            if "user_id" in dir(model):
                print(f"{model.user_id = } | {levels = }")
            return return_json
        return_json["status_code"] = fake_ability["status_code"]
        return_json["response_json"] = fake_ability["message"]
        return return_json

    def update(self, request, session: TestingSessionLocal, fake_ability: dict):
        new_model = Tools.get_class_from_string(schemas, f"{self.class_name}Update")()
        new_name_model_key = f"new_{self.name}"
        return_json = {
            self.name_model_id: 0,
            new_name_model_key: new_model.model_dump(),
            "status_code": status.HTTP_401_UNAUTHORIZED,
        }
        if fake_ability["response"]:
            role = fake_ability["role"]
            user = schemas.user.UserComplete.model_validate(fake_ability["user"])
            if role != "admin" and request.param in ["not_found", "invalid_manager"]:
                return_json["response_json"] = {
                    "detail": i18n.t(self.message_invalid_role)
                }
                return return_json
            elif request.param == "not_found":
                return_json["status_code"] = status.HTTP_404_NOT_FOUND
                return_json["response_json"] = {
                    "detail": i18n.t(
                        self.message_not_found, name=i18n.t(self.message_model_name)
                    )
                }
                return return_json

            levels = get_levels(session, role, user, self.owner)
            model = (
                getattr(fake_model, self.fake_method_name)(session, **levels)
                if self.name_model_id not in levels
                or levels[self.name_model_id] is None
                else Tools.get_class_from_string(models, self.class_name).find_by(
                    session, id=levels[self.name_model_id]
                )
            )
            return_json[self.name_model_id] = model.id
            for attribute in self.update_attributes:
                if request.param == f"update_{attribute}":
                    fake_attribute = SwitchFake.fake(
                        attribute_type=self.attributes[attribute]
                    )
                    return_json[new_name_model_key][attribute] = fake_attribute
                    return_json["status_code"] = status.HTTP_200_OK
            if request.param == "invalid_manager":
                return_json["status_code"] = status.HTTP_200_OK
            return return_json
        return_json["status_code"] = fake_ability["status_code"]
        return_json["response_json"] = fake_ability["message"]
        return return_json

    def delete(self, request, session: TestingSessionLocal, fake_ability: dict):
        return_json = {
            "status_code": status.HTTP_404_NOT_FOUND,
            "response_json": {
                "detail": i18n.t(
                    self.message_not_found, name=i18n.t(self.message_model_name)
                )
            },
        }
        if self.ids_join:
            for id_join in self.ids_join:
                return_json[id_join] = 0
        else:
            return_json[self.name_model_id] = 0
        if fake_ability["response"]:
            role = fake_ability["role"]
            user = schemas.user.UserComplete.model_validate(fake_ability["user"])
            if role != "admin" and request.param != "valid_params":
                return_json["status_code"] = status.HTTP_401_UNAUTHORIZED
                return_json["response_json"] = {
                    "detail": i18n.t(self.message_invalid_role)
                }
                return return_json
            if request.param == "not_found":
                return return_json
            levels = get_levels(session, role, user, self.owner)
            model_fake = (
                getattr(fake_model, self.fake_method_name)(session, **levels)
                if self.name_model_id not in levels
                or levels[self.name_model_id] is None
                else Tools.get_class_from_string(models, self.class_name).find_by(
                    session, id=levels[self.name_model_id]
                )
            )
            print("////////////////////////////")
            print(f"{model_fake = } | {user = } | {levels = } | {role = }")
            if self.ids_join:
                for id_join in self.ids_join:
                    return_json[id_join] = getattr(model_fake, id_join)
            else:
                return_json[self.name_model_id] = model_fake.id
            return_json["status_code"] = status.HTTP_200_OK
            return_json["response_json"] = {"message": True}
            return return_json
        return_json["status_code"] = fake_ability["status_code"]
        return_json["response_json"] = fake_ability["message"]
        return return_json

    def list_test(
        self, client: TestClient, session: TestingSessionLocal, fake_list: dict
    ):
        response = client.get(f"/v1/{self.name}{fake_list['list_attribute']}")
        check.equal(response.status_code, fake_list["status_code"])
        if "response_json" in fake_list:
            check.equal(response.json(), fake_list["response_json"])
        else:
            check.is_instance(response.json(), list)

    def create_test(
        self, client: TestClient, session: TestingSessionLocal, fake_create: dict
    ):
        response = client.post(
            f"/v1/{self.name}/", json=fake_create[self.name_model_key]
        )
        check.equal(response.status_code, fake_create["status_code"])
        if "response_json" in fake_create:
            check.equal(response.json(), fake_create["response_json"])
        else:
            model_class = Tools.get_class_from_string(models, self.class_name)
            if self.ids_join:
                query = {}
                for id_join in self.ids_join:
                    query[id_join] = fake_create[self.name_model_key][id_join]
                model = model_class.find_by(session, **query).as_dict()
            else:
                model = (
                    session.query(model_class)
                    .order_by(model_class.id.desc())
                    .first()  # TODO : REVIEW return None ???
                    .as_dict()
                )
            for attribute in model_class.__table__.columns.keys():
                model_attribute = get_model_attribute_json(model, attribute)
                check.equal(response.json()[attribute], model_attribute)

    def read_test(
        self, client: TestClient, session: TestingSessionLocal, fake_read: dict
    ):
        id_model = fake_read[self.name_model_id]
        print(f"url : /v1/{self.name}/{id_model}")
        response = client.get(f"/v1/{self.name}/{id_model}")
        check.equal(response.status_code, fake_read["status_code"])
        if "response_json" in fake_read:
            check.equal(response.json(), fake_read["response_json"])
        else:
            model_class = Tools.get_class_from_string(models, self.class_name)
            model = model_class.find_by(session, id=id_model).as_dict()
            for attribute in model_class.__table__.columns.keys():
                model_attribute = get_model_attribute_json(model, attribute)
                check.equal(response.json()[attribute], model_attribute)

    def update_test(
        self, client: TestClient, session: TestingSessionLocal, fake_update: dict
    ):
        id_model = fake_update[self.name_model_id]

        new_model = fake_update[f"new_{self.name}"]
        response = client.put(
            f"/v1/{self.name}/{id_model}",
            json=new_model,
        )
        check.equal(response.status_code, fake_update["status_code"])
        if "response_json" in fake_update:
            check.equal(response.json(), fake_update["response_json"])
        else:
            model_class = Tools.get_class_from_string(models, self.class_name)
            model = model_class.find_by(session, id=id_model).as_dict()
            for attribute in model_class.__table__.columns.keys():
                model_attribute = get_model_attribute_json(model, attribute)
                check.equal(response.json()[attribute], model_attribute)
                if attribute in new_model and new_model[attribute]:
                    check.equal(new_model[attribute], model_attribute)

    def delete_test(self, client: TestClient, fake_delete: dict):
        end_uri = (
            "/".join([str(fake_delete[id_join]) for id_join in self.ids_join])
            if self.ids_join
            else fake_delete[self.name_model_id]
        )
        response = client.delete(f"/v1/{self.name}/{end_uri}")
        check.equal(response.status_code, fake_delete["status_code"])
        check.equal(response.json(), fake_delete["response_json"])
