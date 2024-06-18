[[_TOC_]]

# BaseModel

## Attributes
### _errors
An attribute with the last exception
## Methods
### as_dict(self)
A method to get a dict with the attributes values of the instance except those starting with _.

**Arguments :**
None

**Return :**
A dict

**Example :**
```python
class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  name = Column(Text, nullable=False)
  age = Column(Integer, nullable=False)

  PrimaryKeyConstraint("id")

human = Human(name="John Smith", age=20)
print(human.as_dict()) # output : {'name': 'John Smith', 'age': 20}
```
### delete(self, db: Session)
A method to delete an object from the database.

**Arguments :**
- **db** (*Session*) : the session of the database

**Return :**
True

### save(self, db: Session)
A method to save an object into the database. If the save fail, the attribute *_errors* will contains the errors.

**Arguments :**
- **db** (*Session*) : the session of the database

**Return :**
A boolean

**Example :**
```python
class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  name = Column(Text, nullable=False)
  age = Column(Integer, nullable=False)

  PrimaryKeyConstraint("id")

# some lines to define the session of the database
human = Human(age=20)
print(human.save(db=db)) # output : False
print(human._errors) # output : IntegrityError('(sqlite3.IntegrityError) NOT NULL constraint failed: humans.name')
human.name = "John Smith"
print(human.save(db=db)) # output : True
print(human._errors) # output : None
```
### update(self, db: Session, **columns)
A method to update an object into the database. If the update fail, the attribute *_errors* will contains the errors.

**Arguments :**
- **db** (*Session*) : the session of the database
- **columns** (*keyword arguments*) : keyword arguments with the name of the column to change and the new value to assign

**Return :**
A boolean

**Example :**
```python
class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  name = Column(Text, nullable=False)
  age = Column(Integer, nullable=False)

  PrimaryKeyConstraint("id")

# some lines to define the session of the database and get the instance
print(human) # output : Human(id=1, name=John Smith, age=20)
print(human.update(db=db, name=None)) # output : False
print(human._errors) # output : IntegrityError('(sqlite3.IntegrityError) NOT NULL constraint failed: humans.name')
print(human.update(db=db, wrong_column="test")) # output : False
print(human._errors) # output : ColumnsError('Wrong column name')
print(human.save(db=db, age=21)) # output : True
print(human._errors) # output : None
print(human) # output : Human(id=1, name=John Smith, age=21)
```

## Class methods
### count(cls, db: Session, **columns)
A method to count the number of rows on the table with the requested columns.

**Arguments :**
- **db** (*Session*) : the session of the database
- **columns** (*keyword arguments*) : keyword arguments with the query

**Return :**
An integer


**Example :**
```python
# some lines to define the session of the database and the model
print(Human.count(db)) # output : 0
# some lines to create 2 rows in humans table
print(Human.count(db)) # output : 2
print(Human.count(db, id=1)) # output : 1
```
### create(cls, db: Session, **columns)
A method to create an instance and save it into the database.

**Arguments :**
- **db** (*Session*) : the session of the database
- **columns** (*keyword arguments*) : keyword arguments with the columns and their value

**Return :**
An instance of the class


**Example :**
```python
class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  name = Column(Text, nullable=False)
  age = Column(Integer, nullable=False)

  PrimaryKeyConstraint("id")

# some lines to define the session of the database
human = Human.create(db=db, age=20)
print(human._errors) # output : IntegrityError('(sqlite3.IntegrityError) NOT NULL constraint failed: humans.name')
human = Human.create(db=db, name="John Smith", age=20)
print(human._errors) # output : None
print(human) # output : Human(id=1, name=John Smith, age=20)
```
### delete_all(cls, db: Session, **columns)
A method to delete all the instances corresponding to the requested columns.

**Arguments :**
- **db** (*Session*) : the session of the database
- **columns** (*keyword arguments*) : keyword arguments with the query

**Return :**
The number of the rows deleted


**Example :**
```python
class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  name = Column(Text, nullable=False)
  age = Column(Integer, nullable=False)

  PrimaryKeyConstraint("id")

# some lines to define the session of the database and create human
print(Human.delete_all(db=db, id=1)) # output : 1
print(Human.delete_all(db=db, id=1)) # output : 0
```
### find_by(cls, db: Session, **columns)
A method to find the first instance corresponding to the requested columns.

**Arguments :**
- **db** (*Session*) : the session of the database
- **columns** (*keyword arguments*) : keyword arguments with the query

**Return :**
An instance


**Example :**
```python
class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  name = Column(Text, nullable=False)
  age = Column(Integer, nullable=False)

  PrimaryKeyConstraint("id")

# some lines to define the session of the database and create humans
print(Human.find_by(db=db, id=1)) # output : Human(id=1, name=John Smith, age=20)
print(Human.find_by(db=db, id=-1)) # output : None
print(Human.find_by(db=db)) # output : None
```
### where(cls, db: Session, **columns)
A method to find all the instances corresponding to the requested columns.

**Arguments :**
- **db** (*Session*) : the session of the database
- **columns** (*keyword arguments*) : keyword arguments with the query

**Return :**
A list of instance


**Example :**
```python
class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  name = Column(Text, nullable=False)
  age = Column(Integer, nullable=False)

  PrimaryKeyConstraint("id")

# some lines to define the session of the database and create humans
print(Human.where(db=db, id=1)) # output : [Human(id=1, name=John Smith, age=20)]
print(Human.where(db=db, id=-1)) # output : []
print(Human.where(db=db)) # output : [Human(id=1, name=John Smith, age=20), ...]
```

## Query
To find the object, the query use by default the method `__eq__` but can use all the methods listed in [SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators) by using a dict.
### simple column
A search based on a simple column.

**Example :**
```python
class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  name = Column(Text, nullable=False)
  age = Column(Integer, nullable=False)

  PrimaryKeyConstraint("id")

# some lines to define the session of the database
Human.create(db=db, name="John Smith", age=20)
Human.create(db=db, name="Vanessa Durand", age=50)
print(Human.where(db=db, id=1)) # output : [Human(id=1, name=John Smith, age=20)]
print(Human.where(db=db, name={"ilike": "%OHN%"})) # output : [Human(id=1, name=John Smith, age=20)]
print(Human.where(db=db, id={"in_": [1, 2]})) # output : [Human(id=1, name=John Smith, age=20), Human(id=2, name=Vanessa Durand, age=50)]
print(Human.where(db=db, age={"__gt__": 30})) # output : [Human(id=2, name=Vanessa Durand, age=50)]
print(Human.where(db=db, id=1, age={"__gt__": 30})) # output : []
print(Human.where(db=db, id={"in_": [1, 2]}, age={"__gt__": 30})) # output : [Human(id=2, name=Vanessa Durand, age=50)]
```

### relationship
A search based on a relationship.

**Example :**
```python
class Name(BaseModel):
  __tablename__ = "names"

  id = Column(Integer, primary_key=True)
  firstname = Column(Text, nullable=False)
  lastname = Column(Text, nullable=False)

  PrimaryKeyConstraint("id")

  humans = relationship("Human", back_populates="name")

class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  age = Column(Integer, nullable=False)
  name_id = Column(Integer, ForeignKey("names.id"), nullable=False)

  PrimaryKeyConstraint("id")

  name = relationship("Name", back_populates="humans")

# some lines to define the session of the database
name1 = Name.create(db=db, firstname="John", lastname="Smith")
name2 = Name.create(db=db, firstname="Vanessa", lastname="Durand")
Human.create(db=db, age=20, name_id=name1.id)
Human.create(db=db, age=50, name_id=name2.id)
print(Human.where(db=db, name=name2)) # output : [Human(id=2, age=50, name_id=2)]
print(Human.where(db=db, name={"id": 1})) # output : [Human(id=1, age=20, name_id=1)]
print(Human.where(db=db, name={"id": {"in_": [1, 2]}})) # output : [Human(id=1, age=20, name_id=1), Human(id=2, age=50, name_id=2)]
print(Human.where(db=db, name={"firstname": "Vanessa", "lastname": "Durand"})) # output : [Human(id=2, age=50, name_id=2)]
```
### association proxy
A search based on a association proxy.

**Example :**
```python
class Name(BaseModel):
  __tablename__ = "names"

  id = Column(Integer, primary_key=True)
  firstname = Column(Text, nullable=False)
  lastname = Column(Text, nullable=False)

  PrimaryKeyConstraint("id")

  humans = relationship("Human", back_populates="name")

class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  age = Column(Integer, nullable=False)
  name_id = Column(Integer, ForeignKey("names.id"), nullable=False)

  PrimaryKeyConstraint("id")

  name = relationship("Name", back_populates="humans")

  firstname = association_proxy("name", "firstname")
  lastname = association_proxy("name", "lastname")

# some lines to define the session of the database
name1 = Name.create(db=db, firstname="John", lastname="Smith")
name2 = Name.create(db=db, firstname="Vanessa", lastname="Durand")
Human.create(db=db, age=20, name_id=name1.id)
Human.create(db=db, age=50, name_id=name2.id)
print(Human.where(db=db, firstname="Vanessa")) # output : [Human(id=2, age=50, name_id=2)]
print(Human.where(db=db, firstname="Vanessa", lastname="Durand")) # output : [Human(id=2, age=50, name_id=2)]
print(Human.where(db=db, lastname={"in_": ["Smith", "Toto"]})) # output : [Human(id=1, age=20, name_id=2)]
print(Human.where(db=db, lastname={"like": "Toto"})) # output : []
```
### order by
A key to define the order by.

**Example :**
```python
class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  firstname = Column(Text, nullable=False)
  lastname = Column(Text, nullable=False)
  age = Column(Integer, nullable=False)

  PrimaryKeyConstraint("id")

# some lines to define the session of the database
Human.create(db=db, firstname="John", lastname="Smith", age=30)
Human.create(db=db, firstname="Vanessa", lastname="Durand", age=25)
Human.create(db=db, firstname="John", lastname="Doe", age=27)
print(Human.where(db=db) # output : [Human(id=1, firstname=John, lastname=Smith, age=30), Human(id=2, firstname=Vanessa, lastname=Durand, age=50), Human(id=3, firstname=John, lastname=Doe, age=27)]
print(Human.where(db=db, order_by={"id": "asc"}) # output : [Human(id=1, firstname=John, lastname=Smith, age=30), Human(id=2, firstname=Vanessa, lastname=Durand, age=50), Human(id=3, firstname=John, lastname=Doe, age=27)]
print(Human.where(db=db, order_by={"id": "desc"}) # output : [Human(id=3, firstname=John, lastname=Doe, age=27), Human(id=2, firstname=Vanessa, lastname=Durand, age=50), Human(id=1, firstname=John, lastname=Smith, age=30)]
print(Human.where(db=db, order_by={"age": "asc"}) # output : [Human(id=2, firstname=Vanessa, lastname=Durand, age=50), Human(id=3, firstname=John, lastname=Doe, age=27), Human(id=1, firstname=John, lastname=Smith, age=30)]
print(Human.where(db=db, order_by={"firstname": "asc", "lastname": "asc"}) # output : [Human(id=3, firstname=John, lastname=Doe, age=27), Human(id=1, firstname=John, lastname=Smith, age=30), Human(id=2, firstname=Vanessa, lastname=Durand, age=50)]
```
### options
For now, the only option is `joinedload` to avoid [N+1 problem](https://www.sqlservercentral.com/articles/how-to-avoid-n1-queries-comprehensive-guide-and-python-code-examples).

**Example :**
```python
class Name(BaseModel):
  __tablename__ = "names"

  id = Column(Integer, primary_key=True)
  firstname = Column(Text, nullable=False)
  lastname = Column(Text, nullable=False)

  PrimaryKeyConstraint("id")

  humans = relationship("Human", back_populates="name")

class Human(BaseModel):
  __tablename__ = "humans"

  id = Column(Integer, primary_key=True)
  age = Column(Integer, nullable=False)
  name_id = Column(Integer, ForeignKey("names.id"), nullable=False)

  PrimaryKeyConstraint("id")

  name = relationship("Name", back_populates="humans")
  things = relationship("Thing", back_populates="human")

class Thing(BaseModel):
  __tablename__ = "things"

  id = Column(Integer, primary_key=True)
  name = Column(Text, nullable=False)
  color = Column(Text, nullable=False)
  human_id = Column(Integer, ForeignKey("humans.id"), nullable=False)

  PrimaryKeyConstraint("id")

  human = relationship("Human", back_populates="things")


# some lines to define the session of the database and some object
name = Name.find_by(db=db, id=1)
name.humans # produce again a request to the database
name.humans[0].things # produce again a request to the database

name = Name.find_by(db=db, id=1, options={"humans": "id"})
name.humans # doesn't produce again a request to the database
name.humans[0].things # produce again a request to the database

name = Name.find_by(db=db, id=1, options={"humans": {"join": "things"}})
name.humans # doesn't produce again a request to the database
name.humans[0].things # doesn't produce again a request to the database

name = Name.find_by(db=db, id=1, options={"humans": {"id": 1}})
name.humans # doesn't produce again a request to the database - only humans with id = 1

name = Name.find_by(db=db, id=1, options={"humans": {"join": {"things" : {"color" : "red"}}}})
name.humans # doesn't produce again a request to the database
name.humans[0].things # doesn't produce again a request to the database - only things with color = red
```
