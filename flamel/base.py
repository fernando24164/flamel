from flamel.column import Column
from flamel.query import Query
from flamel.dialect import SQLiteDBAPI


class Base:
    __registry__ = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in Base.__registry__:
            Base.__registry__[cls.__name__] = cls

    @classmethod
    def get_all_models(cls):
        return {name: cls for name, cls in cls.__registry__.items()}

    @classmethod
    def get_model(cls, name):
        return cls.__registry__.get(name)

    @classmethod
    def create_tables(cls):
        if not hasattr(cls, "engine") or cls.engine is None:
            raise AttributeError(
                "Database engine is not set. Please set the engine before creating tables."
            )

        for model in cls.get_all_models().values():
            columns = []

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

            for name, attr in model.__dict__.items():
                if isinstance(attr, Column) and attr.foreign_key is not None:
                    foreign_key_def = f"FOREIGN KEY ({attr.foreign_key.column_name}) REFERENCES {attr.foreign_key.referenced_table}({attr.foreign_key.referenced_column})"
                    columns.append(foreign_key_def)

            table_name = model.__name__
            columns_str = ", ".join(columns)
            cls.engine.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str});"
            )

    @classmethod
    def set_engine(cls, engine: str):
        cls.engine = SQLiteDBAPI(engine)

    @classmethod
    def engine_close(cls):
        cls.engine.close()

    @classmethod
    def query(cls):
        return Query(cls, cls.engine)
