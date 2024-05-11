from unittest import TestCase
from unittest.mock import MagicMock, patch

from flamel.base import Base
from flamel.column import Column, Integer, String, ForeignKey
from flamel.query import Query, SQLQueryBuilder


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
        query = SubClass5.query().select("id", "name", "age").order_by("name", "age", direction="DESC")
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
            query = SubClass8.query().join("LEFT", "SubClass7", "SubClass8.sub_class7_id = SubClass7.id")
            query = str(query)

    def test_sql_builder_multiple_joins(self):
        class SubClass9(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            name = Column("name", String, nullable=False)

        class SubClass10(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            sub_class9_id = Column("sub_class9_id", Integer, foreign_key=ForeignKey("sub_class9_id", "SubClass9", "id"))

        class SubClass11(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            sub_class10_id = Column("sub_class10_id", Integer, foreign_key=ForeignKey("sub_class10_id", "SubClass10", "id"))

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
