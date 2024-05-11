import sqlite3
import unittest

from flamel.dialect import SQLiteDBAPI


class TestConnection(unittest.TestCase):
    def test_connect_and_create_cursor(self):
        database = ":memory:"

        with SQLiteDBAPI(database) as db:
            assert db.conn is not None
            assert db.cursor is not None

    def test_invalid_sql_exception(self):
        database = ":memory:"
        invalid_sql = "SELECT * FROM non_existent_table"

        with SQLiteDBAPI(database) as db:
            with self.assertRaises(sqlite3.OperationalError):
                db.execute(invalid_sql)
