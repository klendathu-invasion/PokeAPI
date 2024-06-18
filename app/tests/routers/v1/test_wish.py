import pytest

from ...test_main import TestClient, TestingSessionLocal, client, session
from ...utils.fake_model import fake_ability, fake_auth_user
from ...utils.router_fake import RouterFake

wish_fake_test = RouterFake(
    name="wish",
    uniq_attribute="attributes.name",
    owner="client",
    parents=["user"],
    attributes={"name": "str", "user_id": "id"},
    tablename="wishes",
    update_attributes=["name"],
)


@pytest.fixture(params=["created", "invalid_manager", "already_exist"])
def _fake_create_wish(request, session: TestingSessionLocal, fake_ability: dict):
    return wish_fake_test.create(request, session, fake_ability)


@pytest.fixture(params=["not_found", "valid_manager", "invalid_manager"])
def _fake_read_wish(request, session: TestingSessionLocal, fake_ability: dict):
    return wish_fake_test.read(request, session, fake_ability)


@pytest.fixture(params=["not_found", "valid_manager", "invalid_manager"])
def _fake_list_wishes_by_user(
    request, session: TestingSessionLocal, fake_ability: dict
):
    return wish_fake_test.list(request, session, fake_ability, "user")


@pytest.fixture(params=["not_found", "invalid_manager", "update_name"])
def _fake_update_wish(request, session: TestingSessionLocal, fake_ability: dict):
    return wish_fake_test.update(request, session, fake_ability)


@pytest.fixture(params=["not_found", "invalid_manager", "valid_params"])
def _fake_delete_wish(request, session: TestingSessionLocal, fake_ability: dict):
    return wish_fake_test.delete(request, session, fake_ability)


def test_create_wish(
    client: TestClient, session: TestingSessionLocal, _fake_create_wish: dict
):
    return wish_fake_test.create_test(client, session, _fake_create_wish)


def test_read_wish(
    client: TestClient, session: TestingSessionLocal, _fake_read_wish: dict
):
    return wish_fake_test.read_test(client, session, _fake_read_wish)


def test_list_wishes_by_user(
    client: TestClient,
    session: TestingSessionLocal,
    _fake_list_wishes_by_user: dict,
):
    return wish_fake_test.list_test(client, session, _fake_list_wishes_by_user)


def test_update_wish(
    client: TestClient, session: TestingSessionLocal, _fake_update_wish: dict
):
    return wish_fake_test.update_test(client, session, _fake_update_wish)


def test_delete_wish(client: TestClient, _fake_delete_wish: dict):
    return wish_fake_test.delete_test(client, _fake_delete_wish)
