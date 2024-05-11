import unittest
from datetime import datetime
from unittest.mock import MagicMock, call

from flamel.base import Base
from flamel.column import Column, DateTime, Integer, String, ForeignKey


class TestBase(unittest.TestCase):
    def setUp(self):
        self.db_mock = MagicMock()
        Base.engine = self.db_mock

    def tearDown(self) -> None:
        Base.__registry__.clear()
        return super().tearDown()

    def test_init_subclass(self):
        class SubClass(Base):
            pass

        self.assertIn(SubClass.__name__, Base.__registry__)

    def test_get_all_models(self):
        class SubClass1(Base):
            pass

        class SubClass2(Base):
            pass

        models = Base.get_all_models()
        self.assertIn(SubClass1.__name__, models)
        self.assertIn(SubClass2.__name__, models)

    def test_get_model(self):
        class SubClass3(Base):
            pass

        models = Base.get_model(SubClass3.__name__)
        self.assertEqual(SubClass3, models)

    def test_create_tables(self):

        class SubClass4(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            name = Column("name", String, nullable=False, unique=True)

        Base.create_tables()
        self.db_mock.execute.assert_called_once_with(
            "CREATE TABLE IF NOT EXISTS SubClass4 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);"
        )

    def test_create_tables_with_foreign_key(self):
        class ParentClass(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            name = Column("name", String, nullable=False, unique=True)

        class ChildClass(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            parent_id = Column(
                "parent_id", Integer, foreign_key=ForeignKey('parent_id', "ParentClass", "id")
            )

        Base.create_tables()
        self.db_mock.execute.assert_has_calls(
            [
                call(
                    "CREATE TABLE IF NOT EXISTS ParentClass (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);"
                ),
                call(
                    "CREATE TABLE IF NOT EXISTS ChildClass (id INTEGER PRIMARY KEY AUTOINCREMENT, parent_id INTEGER, FOREIGN KEY (parent_id) REFERENCES ParentClass(id));"
                ),
            ],
            any_order=True,
        )

    def test_create_tables_with_check_constraint(self):
        class Worker(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            age = Column("age", Integer, check="age >= 0")

        Base.create_tables()
        self.db_mock.execute.assert_called_once_with(
            "CREATE TABLE IF NOT EXISTS Worker (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER CHECK (age >= 0));"
        )

    def test_create_tables_with_default_value(self):
        class MyClass2(Base):
            id = Column("id", Integer, primary_key=True, autoincrement=True)
            created_at = Column("created_at", DateTime, default=datetime.now)

        Base.create_tables()
        self.db_mock.execute.assert_called_once_with(
            "CREATE TABLE IF NOT EXISTS MyClass2 (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);"
        )
