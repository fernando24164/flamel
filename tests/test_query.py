from unittest import TestCase
from unittest.mock import MagicMock, patch

from flamel.base import Base
from flamel.column import Column, Integer, String, ForeignKey
from flamel.query import Query, SQLQueryBuilder, validate_sql


class TestQuery(TestCase):
    def test_initializes_query_builder_attribute(self):
        model = "TestModel"
        conn = "TestConnection"
        query = Query(model, conn)
        assert isinstance(query.query_builder, SQLQueryBuilder)

    def test_select_specific_columns(self):
        class SubClass1(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            name = Column("name", String, nullable=False)

        model = SubClass1
        mock_conn = MagicMock()

        expected_result = [(1, "row_name1"), (2, "row_name2")]

        with patch("flamel.query.Query.execute") as mock_execute:
            mock_execute.return_value = expected_result
            query = Query(model, mock_conn)
            result = query.select("column1", "column2").execute()
            assert result == expected_result
            mock_execute.assert_called_once()

    def test_filter_called_before_select(self):
        model = "TestModel"
        conn = MagicMock()
        query = Query(model, conn)
        with self.assertRaises(ValueError):
            query.filter(name="John")

    def test_sql_builder_filter(self):
        class SubClass2(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            name = Column("name", String, nullable=False)

        Base.set_engine(":memory:")
        query = SubClass2.query().select("id", "name").filter(name="test")
        query = str(query)
        assert query == "SELECT id, name FROM SubClass2 WHERE name = ?, ['test']"

    def test_sql_builder_empty_filter(self):
        class SubClass3(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            name = Column("name", String, nullable=False)

        Base.set_engine(":memory:")
        query = SubClass3.query().select("id", "name").filter()
        query = str(query)
        assert query == "SELECT id, name FROM SubClass3"

    def test_sql_builder_order_by_multiple_columns(self):
        class SubClass5(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            name = Column("name", String, nullable=False)
            age = Column("age", Integer, nullable=False)

        Base.set_engine(":memory:")
        query = (
            SubClass5.query()
            .select("id", "name", "age")
            .order_by("name", "age", direction="DESC")
        )
        query = str(query)
        assert query == "SELECT id, name, age FROM SubClass5 ORDER BY name, age DESC"

    def test_sql_builder_limit_and_offset(self):
        class SubClass6(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            name = Column("name", String, nullable=False)
            age = Column("age", Integer, nullable=False)

        Base.set_engine(":memory:")
        Base.create_tables()
        query = SubClass6.query().select("id", "name", "age").limit(10, offset=20)
        query = str(query)
        assert query == "SELECT id, name, age FROM SubClass6 LIMIT 10 OFFSET 20"

    def test_sql_builder_join_without_select(self):
        class SubClass7(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            name = Column("name", String, nullable=False)

        class SubClass8(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            sub_class7_id = Column(
                "sub_class7_id",
                Integer,
                foreign_key=ForeignKey("sub_class7_id", "SubClass7", "id"),
            )

        Base.set_engine(":memory:")

        with self.assertRaises(ValueError):
            query = SubClass8.query().join(
                "LEFT", "SubClass7", "SubClass8.sub_class7_id = SubClass7.id"
            )
            query = str(query)

    def test_sql_builder_multiple_joins(self):
        class SubClass9(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            name = Column("name", String, nullable=False)

        class SubClass10(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            sub_class9_id = Column(
                "sub_class9_id",
                Integer,
                foreign_key=ForeignKey("sub_class9_id", "SubClass9", "id"),
            )

        class SubClass11(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            sub_class10_id = Column(
                "sub_class10_id",
                Integer,
                foreign_key=ForeignKey("sub_class10_id", "SubClass10", "id"),
            )

        Base.set_engine(":memory:")

        query = (
            SubClass11.query()
            .select("SubClass11.id", "SubClass9.name", "SubClass10.id")
            .join("LEFT", "SubClass10", "SubClass11.sub_class10_id = SubClass10.id")
            .join("LEFT", "SubClass9", "SubClass10.sub_class9_id = SubClass9.id")
        )
        query = str(query)

        assert query == (
            "SELECT SubClass11.id, SubClass9.name, SubClass10.id "
            "FROM SubClass11 "
            "LEFT JOIN SubClass10 ON SubClass11.sub_class10_id = SubClass10.id "
            "LEFT JOIN SubClass9 ON SubClass10.sub_class9_id = SubClass9.id"
        )


class TestValidateSQL(TestCase):
    def test_valid_select_query(self):
        query = "SELECT name, age FROM users WHERE age > 21;"
        self.assertTrue(validate_sql(query), "Valid SELECT query should pass.")

    def test_valid_insert_query(self):
        query = "INSERT INTO users (name, age) VALUES ('Alice', 30);"
        self.assertTrue(validate_sql(query), "Valid INSERT query should pass.")

    def test_invalid_sql_missing_keyword(self):
        query = "SELECT name, age users WHERE age > 21;"
        with self.assertRaises(ValueError) as context:
            validate_sql(query)
        self.assertEqual(
            str(context.exception),
            "Invalid SQL: Syntax error or unsupported query type.",
            "Invalid SQL missing keyword should raise ValueError.",
        )

    def test_valid_create_table_query(self):
        query = "CREATE TABLE users (id INT, name VARCHAR(255));"
        self.assertTrue(validate_sql(query), "Valid CREATE TABLE query should pass.")


class MyModel:
    __name__ = "MyModel"


class TestQueryGroupBy(TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.query = Query(MyModel, self.conn)

    def test_group_by_single_column(self):
        self.query.select("column1", "column2").group_by("column1").execute()
        expected_query = "SELECT column1, column2 FROM MyModel GROUP BY column1"
        self.conn.execute.assert_called_with(expected_query, [])

    def test_group_by_multiple_columns(self):
        self.query.select("column1", "column2").group_by("column1", "column2").execute()
        expected_query = (
            "SELECT column1, column2 FROM MyModel GROUP BY column1, column2"
        )
        self.conn.execute.assert_called_with(expected_query, [])

    def test_group_by_without_select(self):
        with self.assertRaises(ValueError) as context:
            self.query.group_by("column1")
        self.assertEqual(
            str(context.exception),
            "The 'select' method must be called before 'group_by'.",
        )

    def test_group_by_no_columns(self):
        self.query.select("column1", "column2").group_by().execute()
        expected_query = "SELECT column1, column2 FROM MyModel GROUP BY "
        self.conn.execute.assert_called_with(expected_query, [])


class TestQueryWithCTE(TestCase):
    def setUp(self):
        self.conn = MagicMock()
        mocked_model = MagicMock()
        mocked_model.__name__ = "cte_example"
        self.query = Query(model=mocked_model, conn=self.conn)

    def test_cte_creation(self):
        cte_name = "cte_example"
        cte_query = "SELECT * FROM example_table"

        self.query.with_cte(cte_name, cte_query)

        expected_query = f"WITH {cte_name} AS ({cte_query}) "
        self.assertEqual(str(self.query), expected_query)

    def test_multiple_ctes(self):
        cte1_name = "cte_example1"
        cte1_query = "SELECT * FROM example_table1"
        cte2_name = "cte_example2"
        cte2_query = "SELECT * FROM example_table2"

        self.query.with_cte(cte1_name, cte1_query)
        self.query.with_cte(cte2_name, cte2_query)

        expected_query = (
            f"WITH {cte2_name} AS ({cte2_query}), WITH {cte1_name} AS ({cte1_query}) "
        )
        self.assertEqual(str(self.query), expected_query)

    def test_cte_integration(self):
        cte_name = "cte_example"
        cte_query = "SELECT * FROM example_table"

        self.query.with_cte(cte_name, cte_query)
        self.query.select("column1", "column2")

        expected_query = (
            f"WITH {cte_name} AS ({cte_query}) SELECT column1, column2 FROM cte_example"
        )
        self.assertEqual(str(self.query), expected_query)


class TestQueryHaving(TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.mock_model = MagicMock()
        self.mock_model.__name__ = "table_example"
        self.query = Query(self.mock_model, self.mock_conn)

    def test_having_with_group_by(self):
        self.query.select("column1", "column2").group_by("column1").having(
            "COUNT(column2) > 1"
        )
        expected_query = "SELECT column1, column2 FROM table_example GROUP BY column1 HAVING COUNT(column2) > 1"
        self.assertEqual(str(self.query), expected_query)

    def test_having_with_multiple_methods(self):
        # Test chaining multiple methods including having
        self.query.select("column1", "column2").group_by("column1").having(
            "COUNT(column2) > 1"
        ).order_by("column1")
        expected_query = "SELECT column1, column2 FROM table_example GROUP BY column1 HAVING COUNT(column2) > 1 ORDER BY column1 ASC"
        self.assertEqual(str(self.query), expected_query)

    def test_having_with_complex_condition(self):
        # Test adding a HAVING clause with a complex condition
        self.query.select("column1", "column2").group_by("column1").having(
            "SUM(column2) > 100 AND AVG(column2) < 50"
        )
        expected_query = "SELECT column1, column2 FROM table_example GROUP BY column1 HAVING SUM(column2) > 100 AND AVG(column2) < 50"
        self.assertEqual(str(self.query), expected_query)
