import pytest

from ...test_main import TestClient, TestingSessionLocal, client, session
from ...utils.fake_model import fake_ability, fake_auth_user
from ...utils.router_fake import RouterFake

cart_fake_test = RouterFake(
    name="cart",
    # uniq_attribute="attributes.name",
    owner="client",
    parents=["user", "product"],
    attributes={"quantity": "int", "user_id": "id", "product_id": "id"},
    tablename="carts",
    update_attributes=["quantity"],
)


@pytest.fixture(params=["created", "already_exist"])
def _fake_create_cart(request, session: TestingSessionLocal, fake_ability: dict):
    return cart_fake_test.create(request, session, fake_ability)


@pytest.fixture(params=["not_found", "valid_manager", "invalid_manager"])
def _fake_read_cart(request, session: TestingSessionLocal, fake_ability: dict):
    return cart_fake_test.read(request, session, fake_ability)


@pytest.fixture(params=["not_found", "valid_manager", "invalid_manager"])
def _fake_list_carts_by_user(request, session: TestingSessionLocal, fake_ability: dict):
    return cart_fake_test.list(request, session, fake_ability, "user")


@pytest.fixture(params=["not_found", "invalid_manager", "update_quantity"])
def _fake_update_cart(request, session: TestingSessionLocal, fake_ability: dict):
    return cart_fake_test.update(request, session, fake_ability)


@pytest.fixture(params=["not_found", "invalid_manager", "valid_params"])
def _fake_delete_cart(request, session: TestingSessionLocal, fake_ability: dict):
    return cart_fake_test.delete(request, session, fake_ability)


def test_create_cart(
    client: TestClient, session: TestingSessionLocal, _fake_create_cart: dict
):
    return cart_fake_test.create_test(client, session, _fake_create_cart)


def test_read_cart(
    client: TestClient, session: TestingSessionLocal, _fake_read_cart: dict
):
    return cart_fake_test.read_test(client, session, _fake_read_cart)


def test_list_carts_by_user(
    client: TestClient,
    session: TestingSessionLocal,
    _fake_list_carts_by_user: dict,
):
    return cart_fake_test.list_test(client, session, _fake_list_carts_by_user)


def test_update_cart(
    client: TestClient, session: TestingSessionLocal, _fake_update_cart: dict
):
    return cart_fake_test.update_test(client, session, _fake_update_cart)


def test_delete_cart(client: TestClient, _fake_delete_cart: dict):
    return cart_fake_test.delete_test(client, _fake_delete_cart)
