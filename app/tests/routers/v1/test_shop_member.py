import pytest

from ...test_main import TestClient, TestingSessionLocal, client, session
from ...utils.fake_model import fake_ability, fake_auth_user
from ...utils.router_fake import RouterFake

shop_member_fake_test = RouterFake(
    name="shop_member",
    uniq_attribute="name",
    owner="pro",
    parents=["shop", "user"],
    ids_join=["shop_id", "user_id"],
    attributes={"shop_id": "id", "user_id": "id"},
    tablename="shop_members",
)


@pytest.fixture(params=["created", "invalid_manager", "already_exist"])
def _fake_create_shop_member(request, session: TestingSessionLocal, fake_ability: dict):
    return shop_member_fake_test.create(request, session, fake_ability)


@pytest.fixture(params=["not_found", "invalid_manager", "valid_params"])
def _fake_delete_shop_member(request, session: TestingSessionLocal, fake_ability: dict):
    return shop_member_fake_test.delete(request, session, fake_ability)


def test_create_shop_member(
    client: TestClient, session: TestingSessionLocal, _fake_create_shop_member: dict
):
    return shop_member_fake_test.create_test(client, session, _fake_create_shop_member)


def test_delete_shop_member(client: TestClient, _fake_delete_shop_member: dict):
    return shop_member_fake_test.delete_test(client, _fake_delete_shop_member)
