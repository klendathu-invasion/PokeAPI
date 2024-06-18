[[_TOC_]]

# How to create a test

Here is the page to create a new test in the project. If you don't have a router, go to the page to [create a router](./wiki/process_router.md "how to create a router").

## Tests

### Step

- Create a faker of your model in `app/tests/utils/fake_model.py`.
- Create a file in the `app/tests/models` repository to create your model tests.
- Create a file in the `app/tests/routers/vX` repository (X will be the number of the version for the endpoints).
- Create tests for your endpoints.

### Example

Let's take the models `human` and `life_item` created in the [previous page](./wiki/process_model.md "how to create a model").

#### Create a fake model

Let's start by adding their faker model in `app/tests/utils/fake_model.py` :
```python
# some lines
def fake_human(session: TestingSessionLocal, **columns_ids):
    name = fake.name().title()
    age = fake.pyint()
    human_json = {
        "name": name,
        "age": age,
    }
    return models.human.Human.create(session, **human_json)

def fake_life_item(session: TestingSessionLocal, **columns_ids):
    name = fake.name()
    human_id = (
        columns_ids["human_id"]
        if "human_id" in columns_ids and isinstance(columns_ids["human_id"], int)
        else fake_human(session).id
    )
    life_item_json = {"name": name, "human_id": human_id}
    return models.life_item.LifeItem.create(session, **life_item_json)
# some other lines
```

Well, now we can create the tests file.

#### Models Tests

First, create the file `app/tests/models/test_human.py` to test `human` model :
```python
from sqlalchemy.orm.decl_api import DeclarativeMeta

from ... import models
from ..test_main import session
from .model_test import ModelTest


class TestHuman(ModelTest):
    class_name: str = "human"
    fake_model: str = "fake_human"
    class_model: DeclarativeMeta = models.human.Human
    default_columns: dict = {
        "name": "str",
        "age": "int",
    }
    like_test: str = "name"
    option_relation_test: str = "life_items"

    # others tests can be define here
```

Next, create the file `app/tests/models/test_life_item.py` to test `life_item` model :
```python
from sqlalchemy.orm.decl_api import DeclarativeMeta

from ... import models
from ..test_main import session
from .model_test import ModelTest


class TestLifeItem(ModelTest):
    class_name: str = "life_item"
    fake_model: str = "fake_life_item"
    class_model: DeclarativeMeta = models.life_item.LifeItem
    default_columns: dict = {
        "name": "str",
        "human": "model",
    }
    like_test: str = "name"
    relations: list[str] = ["human"]

    # others tests can be define here
```

#### Routers Tests

Let's take the routers `human` and `life_item` created in the [previous page](./wiki/process_router.md "how to create a router").

Create the file `app/tests/routers/v1/test_human.py` to test `human` router :
```python
import pytest

from ...test_main import client
from ...test_main import fake
from ...test_main import session
from ...test_main import TestClient
from ...test_main import TestingSessionLocal
from ...utils.fake_model import fake_ability
from ...utils.fake_model import fake_auth_user
from ...utils.router_fake import RouterFake

human_fake_test = RouterFake(
    name="human",
    parents=[],
    attributes={"name": "name", "age": "int"},
    tablename="humans",
    update_attributes=["age"],
)


@pytest.fixture(params=["created", "invalid_manager"])
def _fake_create_human(request, session: TestingSessionLocal, fake_ability: dict):
    return human_fake_test.create(request, session, fake_ability)


@pytest.fixture(params=["not_found", "valid_manager", "invalid_manager"])
def _fake_read_human(request, session: TestingSessionLocal, fake_ability: dict):
    return human_fake_test.read(request, session, fake_ability)


@pytest.fixture(params=["not_found", "invalid_manager", "update_end_time"])
def _fake_update_human(request, session: TestingSessionLocal, fake_ability: dict):
    return human_fake_test.update(request, session, fake_ability)


@pytest.fixture(params=["not_found", "invalid_company_manager", "valid_params"])
def _fake_delete_human(request, session: TestingSessionLocal, fake_ability: dict):
    return human_fake_test.delete(request, session, fake_ability)


def test_create_human(
    client: TestClient, session: TestingSessionLocal, _fake_create_human: dict
):
    return human_fake_test.create_test(client, session, _fake_create_human)


def test_read_human(
    client: TestClient, session: TestingSessionLocal, _fake_read_human: dict
):
    return human_fake_test.read_test(client, session, _fake_read_human)


def test_update_human(
    client: TestClient, session: TestingSessionLocal, _fake_update_human: dict
):
    return human_fake_test.update_test(client, session, _fake_update_human)


def test_delete_human(client: TestClient, _fake_delete_human: dict):
    return human_fake_test.delete_test(client, _fake_delete_human)

```

And now the file `app/tests/routers/v1/test_life_item.py` to test `life_item` router :
```python
import pytest

from ...test_main import client
from ...test_main import session
from ...test_main import TestClient
from ...test_main import TestingSessionLocal
from ...utils.fake_model import fake_ability
from ...utils.fake_model import fake_auth_user
from ...utils.router_fake import RouterFake

life_item_fake_test = RouterFake(
    name="life_item",
    uniq_attribute="attributes.name",
    parents=["human"],
    attributes={"name": "name", "description": "str", "human_id": "id"},
    tablename="life_items",
    update_attributes=["name"],
)


@pytest.fixture(params=["invalid_manager", "valid_manager"])
def _fake_list_life_items(request, session: TestingSessionLocal, fake_ability: dict):
    return life_item_fake_test.list(request, session, fake_ability, "human")


@pytest.fixture(params=["created", "invalid_manager", "already_exist"])
def _fake_create_life_item(request, session: TestingSessionLocal, fake_ability: dict):
    return life_item_fake_test.create(request, session, fake_ability)


@pytest.fixture(params=["not_found", "valid_manager", "invalid_manager"])
def _fake_read_life_item(request, session: TestingSessionLocal, fake_ability: dict):
    return life_item_fake_test.read(request, session, fake_ability)


@pytest.fixture(params=["not_found", "invalid_manager", "update_reference"])
def _fake_update_life_item(request, session: TestingSessionLocal, fake_ability: dict):
    return life_item_fake_test.update(request, session, fake_ability)


@pytest.fixture(params=["not_found", "invalid_company_manager", "valid_params"])
def _fake_delete_life_item(request, session: TestingSessionLocal, fake_ability: dict):
    return life_item_fake_test.delete(request, session, fake_ability)


def test_list_life_items(
    client: TestClient, session: TestingSessionLocal, _fake_list_life_items: dict
):
    return life_item_fake_test.list_test(client, session, _fake_list_life_items)


def test_create_life_item(
    client: TestClient, session: TestingSessionLocal, _fake_create_life_item: dict
):
    return life_item_fake_test.create_test(client, session, _fake_create_life_item)


def test_read_life_item(
    client: TestClient, session: TestingSessionLocal, _fake_read_life_item: dict
):
    return life_item_fake_test.read_test(client, session, _fake_read_life_item)


def test_update_life_item(
    client: TestClient, session: TestingSessionLocal, _fake_update_life_item: dict
):
    return life_item_fake_test.update_test(client, session, _fake_update_life_item)


def test_delete_life_item(client: TestClient, _fake_delete_life_item: dict):
    return life_item_fake_test.delete_test(client, _fake_delete_life_item)

```

As you can see, in those file you can use the class `RouterFake` to generate your tests. You can write more tests too.
