import pytest
import pytest_check as check
from fastapi import status

from .... import models, schemas
from ...test_main import TestClient, TestingSessionLocal, client, fake, session
from ...utils.fake_model import fake_ability, fake_auth_user, fake_user


@pytest.fixture()
def _fake_read_user_me(session: TestingSessionLocal, fake_ability: dict):
    return_json = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "response_json": {"detail": "Invalid role user"},
    }
    if fake_ability["response"]:
        user = fake_ability["user"]
        return_json["user_id"] = user.id
        return_json["status_code"] = status.HTTP_200_OK
        return_json["response_json"] = schemas.user.User.model_validate(
            user
        ).model_dump()
        return return_json
    return_json["status_code"] = fake_ability["status_code"]
    return_json["response_json"] = fake_ability["message"]
    return return_json


@pytest.fixture(params=["created", "already_exist"])
def _fake_create_user(request, session: TestingSessionLocal, fake_ability: dict):
    _matricule = fake.uuid4()
    _first_name = fake.first_name()
    _last_name = fake.last_name()
    _email = f"{_first_name.lower()}.{_last_name.lower()}@gmail.com"
    _user_json = {
        "matricule": _matricule,
        "first_name": _first_name,
        "last_name": _last_name,
        "email": _email,
    }
    return_json = {"user_json": _user_json, "status_code": status.HTTP_201_CREATED}
    if fake_ability["response"]:
        if request.param == "created":
            return return_json
        user = fake_user(session)
        return_json["user_json"]["matricule"] = user.matricule
        return_json["status_code"] = status.HTTP_400_BAD_REQUEST
        return_json["response_json"] = {"detail": "Matricule already registered"}
        return return_json
    return_json["status_code"] = fake_ability["status_code"]
    return_json["response_json"] = fake_ability["message"]
    return return_json


@pytest.fixture
def _fake_get_all_admin(session: TestingSessionLocal, fake_ability: dict):
    return_json = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "response_json": {"detail": "Invalid role user"},
    }
    if fake_ability["response"]:
        return_json["status_code"] = status.HTTP_200_OK
        return_json["response_json"] = [
            schemas.user.UserBase(**model.as_dict()).model_dump()
            for model in models.user.User.where(
                session, admin={"user_id": {"isnot": None}}
            )
        ]
        return return_json
    return_json["status_code"] = fake_ability["status_code"]
    return_json["response_json"] = fake_ability["message"]
    return return_json


@pytest.fixture(params=["not_found", "other", "self"])
def _fake_read_user(request, session: TestingSessionLocal, fake_ability: dict):
    return_json = {
        "user_id": fake.random_int(),
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "response_json": {"detail": "Invalid role user"},
    }
    if fake_ability["response"]:
        user = fake_ability["user"]
        role = fake_ability["role"]
        if request.param == "not_found":
            return_json["user_id"] = 0
            if role == "admin":
                return_json["status_code"] = status.HTTP_404_NOT_FOUND
                return_json["response_json"] = {"detail": "User not found"}
            return return_json
        elif request.param == "other":
            user_fake = fake_user(session)
            return_json["user_id"] = user_fake.id
            if role == "admin":
                return_json["status_code"] = status.HTTP_200_OK
                return_json["response_json"] = schemas.user.User.model_validate(
                    user_fake
                ).model_dump()
                return return_json
            return return_json
        return_json["user_id"] = user.id
        return_json["status_code"] = status.HTTP_200_OK
        return_json["response_json"] = schemas.user.User.model_validate(
            user
        ).model_dump()
        return return_json
    return_json["status_code"] = fake_ability["status_code"]
    return_json["response_json"] = fake_ability["message"]
    return return_json


@pytest.fixture(params=["not_found", "self", "other_true", "other_false"])
def _fake_update_user_is_admin(
    request, session: TestingSessionLocal, fake_ability: dict
):
    return_json = {
        "user_id": fake.random_int(),
        "is_admin": True,
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "response_json": {"detail": "Invalid role user"},
    }
    if fake_ability["response"]:
        if request.param == "not_found":
            return_json["user_id"] = 0
            return_json["status_code"] = status.HTTP_404_NOT_FOUND
            return_json["response_json"] = {"detail": "User not found"}
        elif request.param == "self":
            user = schemas.user.User.model_validate(fake_ability["user"])
            return_json["user_id"] = user.id
            return_json["status_code"] = status.HTTP_403_FORBIDDEN
            return_json["response_json"] = {
                "detail": "User can't change privilege of itself"
            }
        elif request.param == "other_true":
            _user = fake_user(session)
            response_json = schemas.user.User.model_validate(_user).model_dump()
            return_json["user_id"] = _user.id
            return_json["status_code"] = status.HTTP_200_OK
            return_json["response_json"] = response_json
        else:
            _user = fake_user(session)
            return_json["user_id"] = _user.id
            return_json["is_admin"] = False
            return_json["status_code"] = status.HTTP_200_OK
            return_json["response_json"] = schemas.user.User.model_validate(
                _user
            ).model_dump()
        return return_json
    return_json["status_code"] = fake_ability["status_code"]
    return_json["response_json"] = fake_ability["message"]
    return return_json


@pytest.fixture(params=["not_found", "other", "self"])
def _fake_delete_user(request, session: TestingSessionLocal, fake_ability: dict):
    return_json = {
        "user_id": fake.random_int(),
        "status_code": status.HTTP_404_NOT_FOUND,
        "response_json": {"detail": "User not found"},
    }
    if fake_ability["response"]:
        if request.param == "not_found":
            return_json["user_id"] = 0
            return return_json
        elif request.param == "other":
            user_fake = fake_user(session)
            return_json["user_id"] = user_fake.id
            return_json["status_code"] = status.HTTP_200_OK
            return_json["response_json"] = {"message": True}
            return return_json
        user = fake_ability["user"]
        return_json["user_id"] = user.id
        return_json["status_code"] = status.HTTP_403_FORBIDDEN
        return_json["response_json"] = {"detail": "User can't delete itself"}
        return return_json
    return_json["status_code"] = fake_ability["status_code"]
    return_json["response_json"] = fake_ability["message"]
    return return_json


def test_read_user_me(client: TestClient, _fake_read_user_me: dict):
    response = client.get(f"/v1/users/me")
    check.equal(response.status_code, _fake_read_user_me["status_code"])
    check.equal(response.json(), _fake_read_user_me["response_json"])


def test_create_user(
    client: TestClient, session: TestingSessionLocal, _fake_create_user: dict
):
    response = client.post("/v1/users/", json=_fake_create_user["user_json"])
    check.equal(response.status_code, _fake_create_user["status_code"])
    if "response_json" in _fake_create_user:
        check.equal(response.json(), _fake_create_user["response_json"])
    else:
        check.equal(
            response.json(),
            schemas.user.User.model_validate(
                session.query(models.user.User)
                .order_by(models.user.User.id.desc())
                .first()
            ).model_dump(),
        )
        check.equal(
            response.json()["matricule"], _fake_create_user["user_json"]["matricule"]
        )
        check.equal(
            response.json()["first_name"],
            _fake_create_user["user_json"]["first_name"].title(),
        )
        check.equal(
            response.json()["last_name"],
            _fake_create_user["user_json"]["last_name"].upper(),
        )
        check.equal(response.json()["email"], _fake_create_user["user_json"]["email"])


def test_get_all_admin(client: TestClient, _fake_get_all_admin: dict):
    response = client.get(f"/v1/users/all_admin")
    check.equal(response.status_code, _fake_get_all_admin["status_code"])
    check.equal(response.json(), _fake_get_all_admin["response_json"])


def test_read_user(client: TestClient, _fake_read_user: dict):
    response = client.get(f"/v1/users/{_fake_read_user['user_id']}")
    check.equal(response.status_code, _fake_read_user["status_code"])
    check.equal(response.json(), _fake_read_user["response_json"])


def test_update_user_is_admin(client: TestClient, _fake_update_user_is_admin: dict):
    response = client.put(
        f"/v1/users/{_fake_update_user_is_admin['user_id']}/is_admin",
        data={"is_admin": _fake_update_user_is_admin["is_admin"]},
    )
    check.equal(response.status_code, _fake_update_user_is_admin["status_code"])
    check.equal(response.json(), _fake_update_user_is_admin["response_json"])


def test_delete_user(client: TestClient, _fake_delete_user: dict):
    response = client.delete(f"/v1/users/{_fake_delete_user['user_id']}")
    check.equal(response.status_code, _fake_delete_user["status_code"])
    check.equal(response.json(), _fake_delete_user["response_json"])
