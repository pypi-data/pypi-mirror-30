
import pytest

from aiorm.backends.mysql.driver import MySQLDataBaseDriver
from aiorm.orm.connections import Connection
from sample.models import configs


@pytest.fixture()
async def driver(event_loop):
    driver = MySQLDataBaseDriver()

    await driver.initialize(event_loop, configs['mysql'])
    return driver


@pytest.fixture()
async def connection(driver):
    return await driver.connection()


@pytest.mark.asyncio
async def test_get_connection(event_loop):
    driver = MySQLDataBaseDriver()

    await driver.initialize(event_loop, configs['mysql'])

    connection = await driver.connection()
    assert connection is not None
    assert isinstance(connection, Connection)
    assert await connection.execute('SHOW TABLES', None) > 0


@pytest.mark.asyncio
async def test_fixture(driver, connection):
    assert isinstance(driver, MySQLDataBaseDriver)
    assert isinstance(connection, Connection)