import uuid


class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '%s %s %s' % (self.name, self.column_type, 'primary key' if self.primary_key else '')


class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)', null=True, unique=False):
        super().__init__(name, ddl, primary_key, default)


CharField = StringField


class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)


class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)


class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


DateTimeField = FloatField


class TextField(Field):

    def __init__(self, name=None, default=None, null=True):
        super().__init__(name, 'text', False, default)


class UUIDField(Field):

    def __init__(self, name=None, primary_key=False, default=uuid.uuid4):
        super(UUIDField, self).__init__(name, 'VARCHAR(40)', primary_key, lambda: str(default()))


class ForeignKeyField(Field):
    def __init__(self, fk_model, name=None, related_name=None, default=None, null=True):

        self.fk_model = fk_model
        self.releated_name = related_name
        if isinstance(fk_model, str):
            colunm_type = None
        else:
            colunm_type = fk_model.__mappings__[fk_model.__primary_key__].column_type
        super(ForeignKeyField, self).__init__(name, colunm_type, False, default)
