import asyncio
from aiorm.orm.connections import AbstractConnection


class DataBaseDriver(object):
    NAME = 'NONE'

    async def initialize(self, loop: asyncio.AbstractEventLoop, configs):
        raise NotImplementedError()

    async def connection(self) -> AbstractConnection:
        raise NotImplementedError()
