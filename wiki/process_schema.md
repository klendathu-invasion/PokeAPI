[[_TOC_]]

# How to create a schema

Here is the page to create a new schema in the project. If you don't have a model, go to the page to [create a model](./wiki/process_model.md "how to create a model").
If your schema already exist, you can go to the page to [create a router](./wiki/process_router.md "how to create a router").

## Schema

### Step

- Create a file (named as the model) in the `app/schemas` reportory.
- Import `CustomBase` from the module `custom_base` and other necessaries modules
- Create a base class inheriting from `CustomBase` with attributes you need to create an instance
- Create a update class inheriting from `CustomBase` with only the updatable attributes
- Create a class inheriting from the base class of this model with other attributes and with `orm_mode` activated

### Example

Let's take our example in the [model page](./wiki/process_model.md "how to create a model").
The class `Human` will be in the file `app/schemas/human.py` :
```python
from pydantic import StringConstraints
from pydantic import validator
from typing import Annotated

from .custom_base import CustomBase


class HumanUpdate(CustomBase):
    age: int | None = None

class HumanBase(CustomBase):
    name: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    age: int

class Human(HumanBase):
    id: int

    class Config:
        orm_mode = True

class HumanComplete(Human):
    life_item_ids: list[int] = []

    @validator("life_item_ids", pre=True)
    def ids_validator(cls, value) -> list[str]:
        return list(value)
```

And the class `LifeItem` will be in the file `app/schemas/life_item.py` :
```python
from pydantic import StringConstraints
from typing import Annotated

from .custom_base import CustomBase
from .human import Human

class LifeItemUpdate(CustomBase):
    description: Annotated[str | None, StringConstraints(min_length=1, strip_whitespace=True)] = None
    human_id: int | None = None

class LifeItemBase(CustomBase):
    name: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    human_id: int

class LifeItem(LifeItemBase):
    id: int
    description: Annotated[str | None, StringConstraints(min_length=1, strip_whitespace=True)] = None
    human: Human

    class Config:
        orm_mode = True

class LifeItemComplete(LifeItem):
    pass
```

### ⚠️ Warning

We need 4 classes in the schema, respecting the case as the [model page](./wiki/process_model.md "how to create a model") :
- The class "update" `HumanUpdate, LifeItemUpdate` : the class taking updatable attributes.
- The class "base" `HumanBase, LifeItemBase` : the class taking attributes to create the object.
- The class `Human, LifeItem` : the class orm corresponding to the model with argument we'll send to the user.
- The class "complete" `HumanComplete, LifeItemComplete` : the class with additionnal attributes if need more (sometimes useful in others files).
