import unittest
from datetime import datetime

from flamel.column import Blob, Boolean, Column, DateTime, Integer, Real, String


class TestColumn(unittest.TestCase):
    def test_init(self):
        col = Column(
            "id",
            Integer,
            nullable=False,
            default=0,
            primary_key=True,
            autoincrement=True,
        )
        self.assertEqual(col.name, "id")
        self.assertEqual(col.data_type, Integer)
        self.assertEqual(col.nullable, False)
        self.assertEqual(col.default, 0)
        self.assertEqual(col.primary_key, True)
        self.assertEqual(col.unique, False)
        self.assertEqual(col.check, None)
        self.assertEqual(col.autoincrement, True)

    def test_repr(self):
        col = Column("name", String, nullable=False, default="", unique=True)
        self.assertEqual(
            repr(col),
            "Column(name, String, name=name, nullable=False, default=, primary_key=False, unique=True, check=None, autoincrement=False, foreign_key=None)",
        )

    def test_default_value(self):
        col = Column("created_at", DateTime, nullable=False, default=datetime.now())
        self.assertIsInstance(col.default, datetime)

    def test_check_constraint(self):
        col = Column("age", Integer, nullable=False, default=0, check="age >= 0")
        self.assertEqual(col.check, "age >= 0")

    def test_additional_data_types(self):
        col = Column("weight", Real, nullable=False, default=0.0)
        self.assertEqual(col.data_type, Real)
        col = Column("photo", Blob, nullable=True)
        self.assertEqual(col.data_type, Blob)
        col = Column("is_active", Boolean, nullable=False, default=1)
        self.assertEqual(col.data_type, Boolean)
        col = Column("deleted_at", DateTime, nullable=True)
        self.assertEqual(col.data_type, DateTime)

    def test_create_column_with_default_values(self):
        col = Column("name", String)
        self.assertEqual(col.name, "name")
        self.assertEqual(col.data_type, String)
        self.assertTrue(col.nullable)
        self.assertIsNone(col.default)
        self.assertFalse(col.primary_key)
        self.assertFalse(col.unique)
        self.assertIsNone(col.check)
        self.assertFalse(col.autoincrement)

    def test_create_column_with_custom_values(self):
        col = Column(
            "age",
            Integer,
            nullable=False,
            default=0,
            primary_key=True,
            unique=True,
            check="x > 0",
            autoincrement=True,
        )
        self.assertEqual(col.name, "age")
        self.assertEqual(col.data_type, Integer)
        self.assertFalse(col.nullable)
        self.assertEqual(col.default, 0)
        self.assertTrue(col.primary_key)
        self.assertTrue(col.unique)
        self.assertIsNotNone(col.check)
        self.assertTrue(col.autoincrement)

    def test_create_column_with_datetime_type(self):
        col = Column("created_at", DateTime)
        self.assertEqual(col.name, "created_at")
        self.assertEqual(col.data_type, DateTime)

    def test_create_column_with_invalid_data_type(self):
        with self.assertRaises(TypeError):
            Column("name", list)

    def test_create_column_with_invalid_check_function(self):
        with self.assertRaises(TypeError):
            Column("age", Integer, check=lambda x: 1)
