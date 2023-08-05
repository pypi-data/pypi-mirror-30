import logging
from logging import Logger

import aiomysql
from aiocontext import async_contextmanager

from aiorm.orm.query import QueryCompiler, Query, InsertQuery

from abc import abstractmethod, ABCMeta


class AbstractConnection(object, metaclass=ABCMeta):

    @abstractmethod
    async def select(self, query):
        raise NotImplementedError()

    @abstractmethod
    async def insert(self, query):
        raise NotImplementedError()

    @abstractmethod
    async def update(self, query):
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, query):
        raise NotImplementedError()

    @abstractmethod
    async def transaction(self):
        raise NotImplementedError()

    @abstractmethod
    async def begin_transaction(self):
        raise NotImplementedError()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError()

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError()

    @abstractmethod
    async def execute(self, sql, args):
        raise NotImplementedError()


class Connection(AbstractConnection):
    def __init__(self, conn: aiomysql.Connection, compiler: QueryCompiler = None, logger: Logger = None):
        self._connection = conn
        self.compiler = compiler

        self.logger = logger if logger is not None else logging.getLogger('aiorm')
        self.logger.setLevel(logging.DEBUG)

        self._transactions = 0

    @async_contextmanager
    async def transaction(self):
        await self.begin_transaction()

        try:
            yield self
        except Exception as e:
            await self.rollback()
            raise

        try:
            await self.commit()
        except Exception:
            await self.rollback()
            raise

    async def begin_transaction(self):
        self._transactions += 1

    async def commit(self):
        if self._transactions == 1:
            self._connection.commit()

        self._transactions -= 1

    async def rollback(self):
        if self._transactions == 1:
            self._transactions = 0

            await self._connection.rollback()
        else:
            self._transactions -= 1

    def transaction_level(self):
        return self._transactions

    async def execute(self, sql, args=None):
        cursor = await self._connection.cursor()

        await cursor.execute(sql, args)
        affected = cursor.rowcount
        await cursor.close()
        return affected

    async def insert(self, query_or_data):

        if not isinstance(query_or_data, InsertQuery):
            query = InsertQuery(query_or_data)
        else:
            query = query_or_data

        exe_query, args = self.compiler.compile(query)
        async with self._connection.cursor() as cursor:

            await cursor.execute(exe_query, args)

            affected = cursor.rowcount
            await cursor.close()
            return affected

    async def select(self, query):
        if isinstance(query, Query):
            exe_query, args = self.compiler.compile(query)
        else:
            exe_query, args = query, None

        cursor = await self._connection.cursor()

        self.logger.debug(self.compiler.raw_sql(exe_query), args)

        await cursor.execute(exe_query, args)
        rs = await cursor.fetchall()
        await cursor.close()
        return rs

    async def update(self, query):
        exe_query, args = self.compiler.compile(query)
        await self.execute(exe_query, args)

    async def delete(self, query):
        exe_query, args = self.compiler.compile(query)
        await self.execute(exe_query, args)
