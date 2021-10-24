from pony.orm import *


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


#db.generate_mapping()
