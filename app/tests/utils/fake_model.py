from datetime import datetime, timedelta

import pytest
from fastapi import status
from jose import jwt

from ... import models, schemas
from ...config.auth import Auth, _oauth2_scheme
from ...config.constants import TIME_ZONE_APP
from ...config.env import settings
from ...main import app
from ..test_main import TestingSessionLocal, fake, session


def fake_machine(
    session: TestingSessionLocal,
    **columns_ids,
):
    type_machine_id = (
        columns_ids["type_machine_id"]
        if "type_machine_id" in columns_ids
        and isinstance(columns_ids["type_machine_id"], int)
        else fake_type_machine(session).id
    )
    company_id = (
        columns_ids["company_id"]
        if "company_id" in columns_ids and isinstance(columns_ids["company_id"], int)
        else fake_company(session, **columns_ids).id
    )
    machine_json = {
        "type_machine_id": type_machine_id,
        "company_id": company_id,
        "reference": fake.pystr(),
    }
    return models.machine.Machine.create(session, **machine_json)


def fake_cart(session: TestingSessionLocal, **columns_ids):
    quantity = fake.pyint()
    product_id = (
        columns_ids["product_id"]
        if "product_id" in columns_ids and isinstance(columns_ids["product_id"], int)
        else fake_product(session, **columns_ids).id
    )
    user_id = (
        columns_ids["user_id"]
        if "user_id" in columns_ids and isinstance(columns_ids["user_id"], int)
        else fake_user(session, **columns_ids).id
    )
    cart_json = {"quantity": quantity, "product_id": product_id, "user_id": user_id}
    return models.cart.Cart.create(session, **cart_json)


def fake_product(session: TestingSessionLocal, **columns_ids):
    name = fake.pystr()
    price = fake.pyfloat(min_value=0.01)
    shop_id = (
        columns_ids["shop_id"]
        if "shop_id" in columns_ids and isinstance(columns_ids["shop_id"], int)
        else fake_shop(session, **columns_ids).id
    )
    product_json = {"name": name, "price": price, "shop_id": shop_id}
    return models.product.Product.create(session, **product_json)


def fake_role_admin(session: TestingSessionLocal):
    user = fake_user(session)
    models.admin.Admin.create(session, user_id=user.id)
    return user


def fake_role_client(session: TestingSessionLocal):
    return fake_user(session)


def fake_role_member(session: TestingSessionLocal):
    shop_member = fake_shop_member(session)
    return shop_member.members


def fake_role_owner(session: TestingSessionLocal):
    shop = fake_shop(session)
    return shop.user


def fake_role_possessor(session: TestingSessionLocal):
    wish = fake_wish(session)
    return wish.user


def fake_role_pro(session: TestingSessionLocal):
    return fake_user(session, is_pro=True)


def fake_shop(session: TestingSessionLocal, **columns_ids):
    name = fake.pystr()
    user_id = (
        columns_ids["user_id"]
        if "user_id" in columns_ids and isinstance(columns_ids["user_id"], int)
        else fake_user(session, is_pro=True, **columns_ids).id
    )
    shop_json = {"name": name, "user_id": user_id}
    return models.shop.Shop.create(session, **shop_json)


def fake_shop_member(
    session: TestingSessionLocal,
    shop_id: int | None = None,
    user_id: int | None = None,
    **columns_ids,
):
    if shop_id is None:
        shop_id = fake_shop(session).id
    if user_id is None:
        user_id = fake_user(session, is_pro=True, **columns_ids).id
    shop_member_json = {"shop_id": shop_id, "user_id": user_id}
    return models.shop_member.ShopMember.create(session, **shop_member_json)


def fake_type_machine(session: TestingSessionLocal, **columns_ids):
    label = fake.pystr()
    type_machine_json = {"label": label}
    return models.type_machine.TypeMachine.create(session, **type_machine_json)


def fake_user(session: TestingSessionLocal, **columns_ids):
    matricule = fake.uuid4()
    first_name = fake.first_name().title()
    last_name = fake.last_name().upper()
    email = f"{first_name.lower()}.{last_name.lower()}@gmail.com"
    is_pro = (
        columns_ids["is_pro"]
        if "is_pro" in columns_ids and isinstance(columns_ids["is_pro"], bool)
        else False
    )
    user_json = {
        "matricule": matricule,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "is_pro": is_pro,
    }
    return models.user.User.create(session, **user_json)


def fake_wish(session: TestingSessionLocal, **columns_ids):
    name = fake.pystr()
    user_id = (
        columns_ids["user_id"]
        if "user_id" in columns_ids and isinstance(columns_ids["user_id"], int)
        else fake_user(session, **columns_ids).id
    )
    wish_json = {"name": name, "user_id": user_id}
    return models.wish.Wish.create(session, **wish_json)


@pytest.fixture()
def fake_ability(
    request, session: TestingSessionLocal, fake_auth_user: tuple[str, models.user.User]
):
    endpoint = request._pyfuncitem.originalname[5:]
    role, user = fake_auth_user
    return_json = {"response": False}
    if endpoint in Auth.__abilities__:
        if user is None:
            return_json["status_code"] = status.HTTP_401_UNAUTHORIZED
            return_json["message"] = {"detail": "Invalid authentication credentials"}
            return return_json
        print(f"{role = } : {Auth.__abilities__[endpoint] = } | {user = }")
        if role != "admin" and role not in Auth.__abilities__[endpoint]:
            return_json["status_code"] = status.HTTP_401_UNAUTHORIZED
            return_json["message"] = {"detail": "Invalid role user"}
            return return_json
    return_json["response"] = True
    return_json["role"] = role
    return_json["user"] = user
    return return_json


@pytest.fixture(params=[None, "admin", "owner", "member", "pro", "possessor", "client"])
def fake_auth_user(request, session: TestingSessionLocal):
    class TokenCredential:
        def __init__(self, credentials: str):
            self.credentials = credentials

    role = None
    user = None
    if request.param is not None:
        role = request.param
        user = globals()[f"fake_role_{role}"](session)

    def fake_endode_jwt():
        to_encode = {
            "matricule": user.matricule,
            "email": user.email,
            "exp": datetime.now(tz=TIME_ZONE_APP) + timedelta(minutes=2),
        }
        return jwt.encode(
            to_encode, settings.secret_key_jwt, algorithm=settings.algorithm
        )

    def fake_decode_token():
        yield fake_endode_jwt() if user is not None else ""

    app.dependency_overrides[_oauth2_scheme] = fake_decode_token
    yield (role, user)
    del app.dependency_overrides[_oauth2_scheme]
