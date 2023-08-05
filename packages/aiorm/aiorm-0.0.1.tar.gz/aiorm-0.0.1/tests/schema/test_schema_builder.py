from aiorm.orm.schema import SchemaBuilder
from sample.models import DemoUser, DemoUserProfile
from unittest import TestCase


from tests.configtest import format_sql


class TestSchemaBuilderCase(TestCase):
    def setUp(self):
        self.builder = SchemaBuilder()

    def test_schema_builder(self):
        sql = self.builder.create_table(DemoUser)
        assert format_sql(sql) == format_sql("""CREATE TABLE DemoUser 
                          (id VARCHAR(40) PRIMARY KEY,name VARCHAR(100) )
                        """)
        sql = self.builder.drop_table(DemoUser)
        assert format_sql(sql) == format_sql("""DROP TABLE IF EXISTS DemoUser """)

    def test_drop_tables(self):
        sql = self.builder.drop_tables([DemoUser, DemoUserProfile])

    def test_schema_with_foreign(self):
        self.assertRaises(Exception, self.builder.create_tables([DemoUserProfile]))
