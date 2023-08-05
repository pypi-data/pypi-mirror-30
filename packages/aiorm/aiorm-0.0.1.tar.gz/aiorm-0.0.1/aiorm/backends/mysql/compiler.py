from aiorm.orm.query import QueryCompiler, Query, SelectQuery, InsertQuery
from aiorm.orm.utils import create_args_string


class MySQLQueryCompiler(QueryCompiler):
    __template_select__ = "SELECT {query_fields} FROM {_table_name}{_join}{_where}{_order_by}{_limit}{_offset}"
    __template_insert__ = "INSERT INTO {_table_name} ({_fields}) VALUES ({_values})"
    __template_delete__ = "DELETE FROM {_table_name} WHERE {_where}"

    def compile(self, query):
        if isinstance(query, SelectQuery):
            return self.compile_select(query)
        if isinstance(query, InsertQuery):
            return self.compile_insert(query.data)
        return query, None

    def compile_select(self, query: Query):
        join_builds = [x.build() for x in query._join]
        join_str = ' '.join(join_builds)

        if query._where is not None:
            where_strs, where_args = query._where.build()
            query._args.extend(where_args)
            where_strs = ' ' + where_strs
        else:
            where_strs = ''

        orderby_str = ' ORDER BY ' + ' and '.join(query._orderby) if len(query._orderby) > 0 else ''

        limit_str = ' LIMIT {}'.format(query._limit) if query._limit > 0 else ''

        offset_str = ' OFFSET {}'.format(query._offset) if query._offset > 0 else ''
        t = self.__template_select__

        return t.format(query_fields='*',
                        _table_name=query.table_name,
                        _join=join_str,
                        _where=' WHERE' + where_strs if where_strs != '' else '',
                        _order_by=orderby_str,
                        _limit=limit_str,
                        _offset=offset_str), tuple(query._args)

    def compile_insert(self, data):
        table_name = getattr(data, '__table__')
        primary_key = getattr(data, '__primary_key__')
        fields = getattr(data, '__fields__')
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        insert_template = 'insert into `%s` (%s, `%s`) values (%s)' % (
            table_name, ', '.join(escaped_fields), primary_key, create_args_string(len(escaped_fields) + 1))
        args = list(map(data.get_value_or_default, data.__fields__))
        args.append(data.get_value_or_default(data.__primary_key__))
        return insert_template.replace(self.maker, '%s'), tuple(args)

    def compile_update(self, data):
        args = list(map(data.get_value, data.__fields__))
        args.append(data.get_value(data.__primary_key__))
        template = 'update `%s` set %s where `%s`=?' % (
            data.__table__, ', '.join(map(lambda f: '`%s`=?' % (self.__mappings__.get(f).name or f), data.__fields__)),
            data.__primary_key__)
        return template, tuple(args)

    def compile_delete(self, query_or_data):
        pass
