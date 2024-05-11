import unittest

from flamel.query import SQLQueryBuilder


class MyModel:
    pass


class TestSQLQueryBuilder(unittest.TestCase):
    def test_select_all_columns(self):
        query = SQLQueryBuilder.select(MyModel)
        self.assertEqual(query, "SELECT * FROM MyModel")

    def test_select_specific_columns(self):
        query = SQLQueryBuilder.select(MyModel, ["id", "name", "email"])
        self.assertEqual(query, "SELECT id, name, email FROM MyModel")

    def test_filter_with_no_filters(self):
        filter_str, values = SQLQueryBuilder.filter()
        self.assertEqual(filter_str, "")
        self.assertEqual(values, ())

    def test_order_by_multiple_columns_descending(self):
        order_by = SQLQueryBuilder.order_by("name", "email", direction="DESC")
        self.assertEqual(order_by, " ORDER BY name, email DESC")

    def test_limit_with_offset(self):
        limit = SQLQueryBuilder.limit(10, 20)
        self.assertEqual(limit, " LIMIT 10 OFFSET 20")