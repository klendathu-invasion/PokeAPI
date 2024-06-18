import pytest

from ...test_main import TestClient, TestingSessionLocal, client, session
from ...utils.fake_model import fake_ability, fake_auth_user
from ...utils.router_fake import RouterFake

product_fake_test = RouterFake(
    name="product",
    uniq_attribute="attributes.name",
    owner="pro",
    parents=["shop"],
    attributes={"name": "str", "price": "float", "shop_id": "id"},
    tablename="products",
    update_attributes=["name"],
)


@pytest.fixture(params=["created", "invalid_manager", "already_exist"])
def _fake_create_product(request, session: TestingSessionLocal, fake_ability: dict):
    return product_fake_test.create(request, session, fake_ability)


@pytest.fixture(params=["not_found", "valid_manager", "invalid_manager"])
def _fake_read_product(request, session: TestingSessionLocal, fake_ability: dict):
    return product_fake_test.read(request, session, fake_ability)


@pytest.fixture(params=["not_found", "valid_manager"])
def _fake_list_products_by_shop(
    request, session: TestingSessionLocal, fake_ability: dict
):
    return product_fake_test.list(request, session, fake_ability, "shop")


@pytest.fixture(params=["not_found", "invalid_manager", "update_name"])
def _fake_update_product(request, session: TestingSessionLocal, fake_ability: dict):
    return product_fake_test.update(request, session, fake_ability)


@pytest.fixture(params=["not_found", "invalid_manager", "valid_params"])
def _fake_delete_product(request, session: TestingSessionLocal, fake_ability: dict):
    return product_fake_test.delete(request, session, fake_ability)


def test_create_product(
    client: TestClient, session: TestingSessionLocal, _fake_create_product: dict
):
    return product_fake_test.create_test(client, session, _fake_create_product)


def test_read_product(
    client: TestClient, session: TestingSessionLocal, _fake_read_product: dict
):
    return product_fake_test.read_test(client, session, _fake_read_product)


def test_list_products_by_shop(
    client: TestClient,
    session: TestingSessionLocal,
    _fake_list_products_by_shop: dict,
):
    return product_fake_test.list_test(client, session, _fake_list_products_by_shop)


def test_update_product(
    client: TestClient, session: TestingSessionLocal, _fake_update_product: dict
):
    return product_fake_test.update_test(client, session, _fake_update_product)


def test_delete_product(client: TestClient, _fake_delete_product: dict):
    return product_fake_test.delete_test(client, _fake_delete_product)
