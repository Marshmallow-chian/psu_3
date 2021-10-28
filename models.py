from pony.orm import *
from pydantic import BaseModel


db = Database()


class Producer(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=False)
    country = Required(str)
    products = Set('Products')


class Products(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=False)
    price = Required(float)
    description = Optional(str)
    producer = Required(Producer)


#class User(BaseModel):
#    username: str
#    email: Optional[str] = None
#    full_name: Optional[str] = None
#    disabled: Optional[bool] = None

#db.generate_mapping()
