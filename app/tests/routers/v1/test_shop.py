import pytest

from ...test_main import TestClient, TestingSessionLocal, client, session
from ...utils.fake_model import fake_ability, fake_auth_user
from ...utils.router_fake import RouterFake

shop_fake_test = RouterFake(
    name="shop",
    uniq_attribute="attributes.name",
    owner="pro",
    parents=["user"],
    attributes={"name": "str", "user_id": "id"},
    tablename="shops",
    update_attributes=["name"],
)


@pytest.fixture(params=["created", "already_exist"])
def _fake_create_shop(request, session: TestingSessionLocal, fake_ability: dict):
    return shop_fake_test.create(request, session, fake_ability)


@pytest.fixture(params=["not_found", "valid_manager", "invalid_manager"])
def _fake_read_shop(request, session: TestingSessionLocal, fake_ability: dict):
    return shop_fake_test.read(request, session, fake_ability)


@pytest.fixture(params=["not_found", "valid_manager", "invalid_manager"])
def _fake_list_shops_by_user(request, session: TestingSessionLocal, fake_ability: dict):
    return shop_fake_test.list(request, session, fake_ability, "user")


@pytest.fixture(params=["not_found", "invalid_manager", "update_name"])
def _fake_update_shop(request, session: TestingSessionLocal, fake_ability: dict):
    return shop_fake_test.update(request, session, fake_ability)


@pytest.fixture(params=["not_found", "invalid_manager", "valid_params"])
def _fake_delete_shop(request, session: TestingSessionLocal, fake_ability: dict):
    return shop_fake_test.delete(request, session, fake_ability)


def test_create_shop(
    client: TestClient, session: TestingSessionLocal, _fake_create_shop: dict
):
    return shop_fake_test.create_test(client, session, _fake_create_shop)


def test_read_shop(
    client: TestClient, session: TestingSessionLocal, _fake_read_shop: dict
):
    return shop_fake_test.read_test(client, session, _fake_read_shop)


def test_list_shops_by_user(
    client: TestClient,
    session: TestingSessionLocal,
    _fake_list_shops_by_user: dict,
):
    return shop_fake_test.list_test(client, session, _fake_list_shops_by_user)


def test_update_shop(
    client: TestClient, session: TestingSessionLocal, _fake_update_shop: dict
):
    return shop_fake_test.update_test(client, session, _fake_update_shop)


def test_delete_shop(client: TestClient, _fake_delete_shop: dict):
    return shop_fake_test.delete_test(client, _fake_delete_shop)
