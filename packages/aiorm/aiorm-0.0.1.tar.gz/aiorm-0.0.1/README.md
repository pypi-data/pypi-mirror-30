# Norm

A simple orm for asyncio.

## Important

It's just my toy now.

## Usage

``` python3
import asyncio

from norms.drivers import MysqlDataBaseDriver
from norms.models.model_base import Model, StringField
from norms.schema.manager import SchemaManager

configs = {
    'user': 'root',
    'password': 'root',
    'db': 'ncms',
    'port': 3309
}


class Demo2(Model):
    name = StringField(primary_key=True)
    test = StringField()

async def main(loop):
    driver = MysqlDataBaseDriver()
    await driver.initialize(loop=loop, configs=configs)
    db = await driver.get_connection()
    schema = SchemaManager(db)
    await schema.drop_tables([Demo2])
    await schema.create_tables([Demo2])
    await db.insert(Demo2(name="aaa"))


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
```

## LICENSE

The MIT License (MIT)
Copyright (c) 2018 jeremaihloo
