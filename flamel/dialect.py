import sqlite3


class SQLiteDBAPI:
    def __init__(self, database):
        self.conn = sqlite3.connect(database)
        if self.conn is not None:
            self.cursor = self.conn.cursor()
        else:
            raise Exception("Failed to connect to the database.")

    def execute(self, sql, parameters=()):
        try:
            self.cursor.execute(sql, parameters)
            self.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self.rollback()
            raise sqlite3.OperationalError(e)

    def executemany(self, sql, parameters):
        try:
            self.cursor.executemany(sql, parameters)
            self.commit()
        except sqlite3.Error as e:
            self.rollback()
            raise sqlite3.OperationalError(e)

    def executescript(self, sql):
        try:
            self.cursor.executescript(sql)
            self.commit()
        except sqlite3.Error as e:
            self.rollback()
            raise sqlite3.OperationalError(e)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchmany(self, size):
        return self.cursor.fetchmany(size)

    def fetchall(self):
        if self.cursor is None:
            raise Exception("Database cursor is not initialized.")
        return self.cursor.fetchall()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()
