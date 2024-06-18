[[_TOC_]]

# How to create a router

Here is the page to create a new router in the project. If you don't have a schema, go to the page to [create a schema](./wiki/process_schema.md "how to create a schema").
If your router already exist, you can go to the page to [create a test](./wiki/process_test.md "how to create a test").

## Router

### Step

- Add in `app/config/metadata_tag.py` a variable with name and description of the router and add it in the variable list metadata_tags
- Create a file in the `app/routers/vX` repository (X will be the number of the version for the endpoints).
- Import the necessaries modules
- Create a router with the name of the variable for tag
- Create your endpoints
- Add your endpoints in the variable `_abilities` in the file `app/config/auth.py` to define the roles accepted by this endpoint

### Example

Let's take our classes defined in [previous page](./wiki/process_schema.md "how to create a schema") `Human` and `LifeItem`. We need to create a router CRUD for each of them.

We start by creating a tag for each of them in file `app/config/metadata_tag.py` in class `MetadataTag` :
```python
__tag_human__: _MetadataTag = _MetadataTag(
    name="human",
    description="Endpoints related to human data."
)

__tag_life_item__: _MetadataTag = _MetadataTag(
    name="life item",
    description="Endpoints related to life item data."
)
```

Then add those variables in the method `tag_list` of the same class :
```python
# some lines
def tag_list(cls) -> list[_MetadataTag]:
    return [
        # some tags
        cls.__tag_human__.dict(),
        cls.__tag_life_item__.dict(),
        # some other tags
    ]
```

⚠️ We need to add definitions in locales files for translation (or tests will be slowlest). Then add in the file `app/locales/*/models.*.yml` (where * is `en` or `fr`) the following :
```python
  humans:
    name: Human
    attributes:
      name: Name
  life_items:
    name: Life item
    attributes:
      name: Name
```

Now we can create the routers.
For the `Human`, the router will be in file `app/routers/v1/human.py`:
```python
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from sqlalchemy.orm import Session

from ... import schemas
from ...config.auth import Auth
from ...helpers.check_uniq import CheckUniqHelper
from ...helpers.router import RouterModelHelper
from ...utils.dependency import Dependency

router = APIRouter(
    dependencies=[Depends(Auth.check_role_user)],
)

router_human = RouterModelHelper(
    name="human", parents=[], uniq_list=[]
)


@router.post("/", response_model=schemas.human.Human, status_code=status.HTTP_201_CREATED)
def create_human(human: schemas.human.HumanBase, db: Session = Depends(Dependency.get_db)):
    return router_human.create(db, human.dict())


@router.get("/{human_id}", response_model=schemas.human.Human)
def read_human(human_id: int, db: Session = Depends(Dependency.get_db)):
    return router_human.read(db, human_id)


@router.put(
    "/{human_id}",
    response_model=schemas.human.Human,
    description="The endpoint to update information about the human with the requested id.",
    response_description="The human updated",
)
def update_human(
    human_id: int,
    new_human: schemas.human.HumanUpdate,
    db: Session = Depends(Dependency.get_db),
):
    return router_human.update(db, human_id, new_human.dict())


@router.delete("/{human_id}")
def delete_human(human_id: int, db: Session = Depends(Dependency.get_db)):
    return router_human.delete(db, human_id)
```

And for the `LifeItem`, the router will be in file `app/routers/v1/life_item.py`:
```python
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from sqlalchemy.orm import Session

from ... import schemas
from ...config.auth import Auth
from ...helpers.check_uniq import CheckUniqHelper
from ...helpers.router import RouterModelHelper
from ...utils.dependency import Dependency

router = APIRouter(
    dependencies=[Depends(Auth.check_role_user)],
)


uniq_life_item = CheckUniqHelper(
    name="name",
    equal_list=["human_id"],
    ilike_list=["name"],
)
router_life_item = RouterModelHelper(
    name="life_item", parents=["human"], uniq_list=[uniq_life_item]
)


@router.get("/human/{human_id}", response_model=list[schemas.life_item.LifeItem])
def list_life_items(human_id: int, db: Session = Depends(Dependency.get_db)):
    return router_life_item.list(db, query={"human_id": human_id})


@router.post("/", response_model=schemas.life_item.life_item, status_code=status.HTTP_201_CREATED)
def create_life_item(life_item: schemas.life_item.life_itemBase, db: Session = Depends(Dependency.get_db)):
    return router_life_item.create(db, life_item.dict())


@router.get("/{life_item_id}", response_model=schemas.life_item.life_item)
def read_life_item(life_item_id: int, db: Session = Depends(Dependency.get_db)):
    return router_life_item.read(db, life_item_id)


@router.put("/{life_item_id}", response_model=schemas.life_item.life_item)
def update_life_item(
    life_item_id: int,
    new_life_item: schemas.life_item.life_itemUpdate,
    db: Session = Depends(Dependency.get_db),
):
    return router_life_item.update(db, life_item_id, new_life_item.dict())


@router.delete("/{life_item_id}")
def delete_life_item(life_item_id: int, db: Session = Depends(Dependency.get_db)):
    return router_life_item.delete(db, life_item_id)
```

In those files :
- `RouterModelHelper` is a class with a generic CRUD you can use to fast create a new router.
- `CheckUniqHelper` is a class to check unicity of the model.
- You can add more endpoint if you need.

Put the endpoints in variable `__abilities__` in the file `app/config/auth.py` in the class `Auth` :
```python
# some lines
__abilities__ = {
    #some routers

    # v1/human
    "create_human": [],
    "read_human": [],
    "update_human": [],
    "delete_human": [],

    # v1/life_item
    "list_life_items": [],
    "create_life_item": [],
    "read_life_item": [],
    "update_life_item": [],
    "delete_life_item": [],

    #some other routers
}
# some other lines
```
Valid roles are in variable `__roles__` in the class `Role` in the file `app/config/role.py`.
An empty array mean only role `admin` can do this action.
If the endpoint isn't in this variable, all roles can do the action.

In this project, the new table will probably be linked with others tables to define role. Then you need to add in the variable `__tables_by_id__` in the class `Role` in the file `app/config/role.py` something like :
```python
# some lines
class Role(BaseModel):
    __tables_by_id__ = {
        # some keys
        "human_id": {
            "class": "human",
            "table": "humans",
        },
        "life_item_id": {
            "class": "life_item",
            "parent": ["human_id"],
            "table": "life_humans",
        },
        # some other keys
    }
# some other lines
```
