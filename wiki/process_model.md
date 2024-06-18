[[_TOC_]]

# How to create a model

Here is the page to create a new model in the project.
If your model already exist, you can go to the page to [create a schema](./wiki/process_schema.md "how to create a schema").

## Model

### Step

- Create a file (named as the model) in the `app/models` reportory.
- Import the necessaries attributes of module `sqlalchemy` (Column, Integer, ...)
- Import `BaseModel` from the module `base_model`
- Create your class inheriting from `BaseModel`
- Declare the name of the table for this model
- Declare the columns and relationship

### Example

Let's imagine we need 2 classes :
- a class `Human` with attributes `name` and `age`
- a class `LifeItem` with attributes `name` and `description`

A life item is owned by an human.

The class `Human` will be created in file `app/models/human.py` and look like :
```python
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import String
from sqlalchemy.orm import relationship

from .base_model import BaseModel

class Human(BaseModel):
    __tablename__ = "humans"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)

    PrimaryKeyConstraint("id", name="humans_pkey")

    life_items = relationship("LifeItem", back_populates="human")
```

And the class `LifeItem` will be created in file `app/models/life_item.py` :
```python
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import String
from sqlalchemy.orm import relationship

from .base_model import BaseModel

class LifeItem(BaseModel):
    __tablename__ = "life_items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Integer)
    human_id = Column(Integer, ForeignKey("humans.id", ondelete="CASCADE"), nullable=False)

    PrimaryKeyConstraint("id")

    human = relationship("Human", back_populates="life_items")
```

### ⚠️ Warning

- The name of the file is in **snake case** (`life_item`) and the name of the class is the corresponding name in **camel case** (`LifeItem`).
- The name of the table is usually the pluralize of the name of file.
