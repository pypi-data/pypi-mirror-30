import logging

from aiorm.orm.connections import AbstractConnection

_logger = logging.getLogger('aiorm')


class SchemaBuilder(object):
    """ A sql builder for SchemaManager"""

    def create_tables(self, tables):
        return ';'.join([self.create_table(x) for x in tables])

    def create_table(self, table):
        args = []
        for f_name, f in getattr(table, '__mappings__').items():
            args.append(str(f))
        sql = 'CREATE TABLE {} ( {})'.format(getattr(table, '__table__'), ','.join(args))
        return sql

    def drop_tables(self, tables):
        return ';'.join(self.drop_table(x) for x in tables)

    def drop_table(self, table):
        return 'DROP TABLE IF EXISTS {}'.format(getattr(table, '__table__'))


class SchemaManager(object):
    """ To manage tables, do actions linke create_table, drop_table."""

    def __init__(self, connection: AbstractConnection = None, builder: SchemaBuilder = None):
        self.connection = connection
        self.builder = builder

    def initalize(self, connection: AbstractConnection):
        self.connection = connection

    async def show_tables(self):
        sql = 'SHOW TABLES'
        rs = await self.connection.select(sql)

        def get_tables():
            for item in rs:
                yield [x for x in item.values()]

        tables = []
        [tables.extend(x) for x in get_tables()]
        return tables

    async def create_tables(self, tables, safe=True):
        sql = self.builder.create_tables(tables)
        try:
            await self.connection.execute(sql, None)
        except Exception as e:
            _logger.exception(e)
            if not safe:
                raise Exception('Create Table Error')

    async def drop_tables(self, tables, safe=True):
        sql = self.builder.drop_tables(tables)
        try:
            await self.connection.execute(sql)
        except Exception as e:
            _logger.exception(e)
            if not safe:
                raise Exception('DROP TABLE Error')

    async def add_table_column(self, table, column_name, column_type, column_default):
        pass
