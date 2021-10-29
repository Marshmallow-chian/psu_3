import os.path
from fastapi import FastAPI, Body, Depends
from fastapi.security import OAuth2PasswordBearer
import uvicorn
from models import db, Producer, Products# , User
from pony.orm import db_session, commit
from scheme import ProductsOut, ProducerOut, NewProducts, EditProducts, NewProducer, EditProducer, CoolLvL

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
my_db = 'Manufacturer_and_Products.sqlite'


@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.on_event("startup")
async def start_app():
    """Выполняется при старте приложения"""
    # Прежде чем мы сможем сопоставить сущности с базой данных,
    # нам нужно подключиться, чтобы установить соединение с ней.
    # Это можно сделать с помощью метода bind()
    create_db = True
    if os.path.isfile(my_db):
        create_db = False
    db.bind(provider='sqlite', filename=my_db, create_db=create_db)
    db.generate_mapping(create_tables=create_db)


@app.get('/api/products', tags=['products'])
async def get_all_products():  # 1 +
    with db_session:
        products = Products.select()  # преобразуем запрос в SQL, а затем отправим в базу данных
        all_products = []
        for i in products:
            all_products.append(ProductsOut.from_orm(i))
    return all_products


@app.get('/api/product/get_average_products', tags=['products'])
async def get_average(minimum: int, maximum:int):  # 12-
    with db_session:
        products = Products.select(lambda p: minimum <= p.price and p.price <= maximum)[::]  # работает
        all_products = []
        for i in products:
            all_products.append(ProductsOut.from_orm(i))
        return all_products




@app.get('/api/product/{item_id}', tags=['products'])
async def get_product(item_id: int):  # 2 +
    with db_session:
        if Products.exists(id=item_id):
            product = Products.get(id=item_id)
            return ProductsOut.from_orm(product)
        else:
            return 'товара с таким id не существует'


@app.post('/api/product/new', tags=['products'])
async def new_product(n_product: NewProducts = Body(...)):  # 3 +
    with db_session:

        product = n_product.dict()

        if Products.exists(id=int(n_product.id)):
            return 'товар с таким id уже существует'

        if not Producer.exists(id=int(n_product.producer)):
            return 'Производителя с таким id не существует'

        Products(**product)
        commit()
        return n_product


@app.put('/api/product/edit/{item_id}', tags=['products'])
async def edit_product(item_id: int, edit_pr: EditProducts = Body(...)):  # 4 +
    with db_session:
        if Products.exists(id=item_id):
            product = edit_pr.dict(exclude_unset=True, exclude_none=True)
            Products[item_id].set(**product)
            if not Producer.exists(id=edit_pr.producer):
                if edit_pr.producer != None:
                    return 'Производителя с таким id не существует'
            commit()
            return ProductsOut.from_orm(Products[item_id])
        return 'товара с таким id не существует'


@app.delete('/api/product/delete/{item_id}', tags=['products'])
async def delete_product(item_id: int):  # 5 +
    with db_session:
        if Products.exists(id=item_id):
            Products[item_id].delete()
            commit()
            return "Объект удалён"
        return "производителя с таким id не существует"

#----------------------------------------------------------------------------------------


@app.get('/api/producer/get_cool_producers', tags=['producers'])
async def get_cool(cool_level: int):  # 11
    with db_session:
        producer = Producer.select(lambda p: len(p.products) >= cool_level)[::]  # работает
        all_producer = []
        for i in producer:
            all_producer.append(CoolLvL.from_orm(i))
        return all_producer


@app.get('/api/producers', tags=['producers'])
async def get_all_producers():  # 6 +
    with db_session:
        producer = Producer.select()[:]  # преобразуем запрос в SQL, а затем отправим в базу данных
        all_producer = []
        for i in producer:
            all_producer.append(ProducerOut.from_orm(i))
    return all_producer


@app.get('/api/producer/{item_id}', tags=['producers'])
async def get_producer(item_id: int):  # 7 +
    with db_session:
        if Producer.exists(id=item_id):
            producer = Producer.get(id=item_id)
            return ProducerOut.from_orm(producer)
        else:
            return 'товара с таким id не существует'


@app.post('/api/producer/new', tags=['producers'])
async def new_producer(n_producer: NewProducer = Body(...)):  # 8 +
    with db_session:
        producer = n_producer.dict()

        if Producer.exists(id=int(n_producer.id)):
            return 'производитель с таким id уже существует'

        producer = Producer(**producer)
        commit()
        return ProducerOut.from_orm(producer)


@app.put('/api/producer/edit/{item_id}', tags=['producers'])
async def edit_producer(item_id: int, edit_pr: EditProducer = Body(...)):  # 9 +
    with db_session:
        if Producer.exists(id=item_id):
            producer = edit_pr.dict(exclude_unset=True, exclude_none=True)
            Producer[item_id].set(**producer)
            commit()
            return ProducerOut.from_orm(Producer[item_id])
        return 'производителя с таким id не существует'


@app.delete('/api/producer/delete/{item_id}', tags=['producers'])
async def delete_producer(item_id: int):  # 10 +
    with db_session:
        if Producer.exists(id=item_id):
            Producer[item_id].delete()
            commit()
            return "Объект удалён"
        return "производителя с таким id не существует"


@app.get('/api/producer/{item_id}/products', tags=['producers'])
async def sorted_products(item_id: int):  # 13 +
    with db_session:
        if Producer.exists(id=item_id):
            producer = Producer.get(id=item_id)
            pr = producer.products.select().order_by(Products.price)[::]
            return ProducerOut(**(producer.to_dict() | {'products': pr}))
        return 'Производителя с таким id не существует'


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)