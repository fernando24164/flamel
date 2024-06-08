from flamel.column import Column
from flamel.query import Query
from flamel.dialect import SQLiteDBAPI


class Base:
    __registry__ = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in Base.__registry__:
            Base.__registry__[cls.__name__] = cls

    def __init__(self, **kwargs):
        for name, attr in vars(self.__class__).items():
            if isinstance(attr, Column):
                value = kwargs.get(name, attr.default)
                if value is None and not attr.nullable:
                    value = attr.default
                setattr(self, name, value)

    @classmethod
    def get_all_models(cls):
        return {name: cls for name, cls in cls.__registry__.items()}

    @classmethod
    def get_model(cls, name):
        return cls.__registry__.get(name)

    @classmethod
    def create_tables(cls):
        if not hasattr(cls, "engine") or cls.engine is None:
            raise AttributeError("Database engine is not set. Please set the engine before creating tables.")

        for model in cls.get_all_models().values():
            columns = []
            foreign_keys = []

            for name, attr in model.__dict__.items():
                if isinstance(attr, Column):
                    column_def = f"{attr.name} {attr.data_type.type_name}"

                    if not attr.nullable:
                        column_def += " NOT NULL"

                    if attr.default is not None:
                        column_def += f" DEFAULT {attr.default}"

                    if attr.unique:
                        column_def += " UNIQUE"

                    if attr.check is not None:
                        column_def += f" CHECK ({attr.check})"

                    if attr.primary_key:
                        column_def += " PRIMARY KEY"

                    if attr.autoincrement:
                        column_def += " AUTOINCREMENT"

                    columns.append(column_def)

                    if attr.foreign_key is not None:
                        foreign_key_def = f"FOREIGN KEY ({attr.name}) REFERENCES {attr.foreign_key.referenced_table}({attr.foreign_key.referenced_column})"
                        foreign_keys.append(foreign_key_def)

            table_name = model.__name__
            columns.extend(foreign_keys)
            columns_str = ", ".join(columns)
            cls.engine.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str});")

    @classmethod
    def insert(cls, instance):
        if not hasattr(cls, "engine") or cls.engine is None:
            raise AttributeError(
                "Database engine is not set. Please set the engine before inserting data."
            )

        table_name = instance.__class__.__name__
        columns = []
        values = []

        primary_key_column = None
        primary_key_value = None
        primary_key_autoincrement = False

        for name, attr in instance.__class__.__dict__.items():
            if isinstance(attr, Column):
                value = getattr(instance, name)
                if attr.primary_key:
                    primary_key_column = attr.name
                    primary_key_value = value
                    primary_key_autoincrement = attr.autoincrement

                if value is None or isinstance(value, Column):
                    if attr.nullable:
                        value = None
                elif attr.default is not None:
                    value = attr.default
                elif isinstance(value, Column):
                    continue

                columns.append(attr.name)
                values.append(value)

        if not primary_key_autoincrement:
            raise ValueError("Primary key value is not set.")

        columns_str = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in values])

        if primary_key_autoincrement:
            sql_check = f"SELECT COUNT(*) FROM {table_name} WHERE {columns[1]} = ?"
            result = cls.engine.execute(sql_check, [values[1]])[0][0]
        elif primary_key_column:
            sql_check = f"SELECT COUNT(*) FROM {table_name} WHERE {primary_key_column} = ?"
            result = cls.engine.execute(sql_check, [primary_key_value])[0][0]
        else:
            result = 0

        if result > 0:
            set_clause = ", ".join([f"{col} = ?" for col in columns])
            sql_update = (
                f"UPDATE {table_name} SET {set_clause} WHERE {primary_key_column} = ?"
            )
            cls.engine.execute(sql_update, values + [primary_key_value])
        else:
            sql_insert = (
                f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            )
            cls.engine.execute(sql_insert, values)

    @classmethod
    def set_engine(cls, engine: str):
        cls.engine = SQLiteDBAPI(engine)

    @classmethod
    def engine_close(cls):
        cls.engine.close()

    @classmethod
    def query(cls):
        return Query(cls, cls.engine)
