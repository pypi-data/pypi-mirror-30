# Factory Alchemist
Make it easier to create dummy entries in database in tests using SQLAlchemy

# Usage

First you must have all models and session configured on you project
```python
from sqlalchemy import create_engine, MetaData, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///')
metadata = MetaData(bind=engine)
BaseModel = declarative_base(metadata=metadata)
Session = sessionmaker(bind=engine, autoflush=True, autocommit=True)


class Spam(BaseModel):
    __tablename__ = 'spam'

    id = Column(Integer, primary_key=True)
    purpose = Column(String)
    flavor = Column(Integer, nullable=False)


session = Session()
```

Second you must configure your base model on Factory Alchemist:

```python
from factory_alchemist import factory

factory.BaseModel = BaseModel
```


Then you can start creating database entries:
```python
from factory_alchemist import factory

spam_1 = factory.make(session, Spam)
spam_2 = factory.make(session, Spam, purpose='ham')
spam_3 = factory.make(session, Spam, flavor=7)

spam_1.id, spam_1.purpose, spam_1.flavor  # 1, '<random string>', None
spam_2.id  spam_2.purpose, spam_2.flavor  # 2, 'ham', None
spam_3.id  spam_3.purpose, spam_3.flavor  # 3, '<random string>', 7
```


You can also create entries from sqlalchemy's table:
```python
from factory_alchemist import factory

FishTable = Table('fish', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('spam_id', Integer, ForeignKey('spam.id'), nullable=False))

my_fish = factory.make_t(FishTable)
my_fish.id, my_fish.spam_id  # 1, 1
session.query(Spam).count()  # 1
# Yes, it creates all mandatory foreign key entries!
```


Your tests may be something like this:
```python
from unittest import TestCase


class MyTestCase(TestCase):
    def setUp(self):
        self.__rebuild_schema()
        self.session = Session()

    def tearDown(self):
        self.session.close()

    def test_something(self):
        factory.make(self.session, Spam, purpose='dunno')
        self.assertEqual([('dunno',)],
                         self.session.query(Spam.purpose).all())

    def __rebuild_schema():
        if 'sqlite' in metadata.bind.url.drivername:
            metadata.drop_all()
            metadata.create_all()
        else:
            raise Exception('Not running on SQLite. I am afraid of recreating the database')
```

Currently Factory Alchemist supports basic SQLAlchemy's field types

* SmallInteger
* Integer
* BigInteger
* Float
* String
* CHAR
* Boolean
* Date
* DateTime
* Enum

If you want/need to add other types, you can use the `add_type` function.

```python
import json
from sqlalchemy import String, TypeDecorator
from factory_alchemist import factory
from factory_alchemist.generators import rand_word


class Json(TypeDecorator):
  impl = String

  def process_bind_param(self, value, dialect):
    return json.dumps(value)

  def process_result_value(self, value, dialect):
    return json.loads(value)


def generate_json(type_):
    return {rand_word(10): rand_word(10)}


factory.add_type(Json, generate_json)


class Spam(BaseModel):
    __tablename__ = 'spam'
    my_field = Column(Json, nullable=False)


factory.make(session, Spam)
# <Spam (my_field={'dglwvkrkfn': 'tbcewysqwy'})>
```
