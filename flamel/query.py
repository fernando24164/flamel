from typing import Any, Iterable, List, Optional, Tuple, Union


class SQLQueryBuilder:
    @staticmethod
    def select(model: Any, columns: Optional[List[str]] = None) -> str:
        if columns is None or not columns:
            columns = ["*"]

        column_str = ", ".join(columns)
        table_name = model.__name__
        query = f"SELECT {column_str} FROM {table_name}"
        return query

    @staticmethod
    def filter(**filters: Union[str, Any]) -> Tuple[str, Tuple]:
        if not filters:
            return "", ()

        filter_str = " AND ".join([f"{key} = ?" for key in filters])
        values = tuple(filters.values())
        return filter_str, values

    @staticmethod
    def join(join_type: str, table_name: str, on_condition: str) -> str:
        return f" {join_type} JOIN {table_name} ON {on_condition}"

    @staticmethod
    def order_by(*columns: Iterable[str], direction: str = "ASC") -> str:
        column_str = ", ".join(columns)
        return f" ORDER BY {column_str} {direction}"

    @staticmethod
    def limit(limit: int, offset: Optional[int] = None) -> str:
        if offset is None:
            return f" LIMIT {limit}"
        else:
            return f" LIMIT {limit} OFFSET {offset}"


class Query:
    def __init__(self, model, conn):
        self.model = model
        self.conn = conn
        self.query_builder = SQLQueryBuilder()
        self.query = None
        self.values = []

    def select(self, *columns):
        self.query = self.query_builder.select(self.model, list(columns))
        return self

    def filter(self, **filters):
        if self.query is None:
            raise ValueError("The 'select' method must be called before 'filter'.")
        filter_clause, filter_values = self.query_builder.filter(**filters)
        if filter_clause:
            self.query += f" WHERE {filter_clause}"
        self.values.extend(filter_values)
        return self

    def join(self, join_type, table_name, on_condition):
        if self.query is None:
            raise ValueError("The 'select' method must be called before 'join'.")
        self.query += self.query_builder.join(join_type, table_name, on_condition)
        return self

    def order_by(self, *columns, direction="ASC"):
        if self.query is None:
            raise ValueError("The 'select' method must be called before 'order_by'.")
        self.query += self.query_builder.order_by(*columns, direction=direction)
        return self

    def limit(self, limit, offset=None):
        if self.query is None:
            raise ValueError("The 'select' method must be called before 'limit'.")
        self.query += self.query_builder.limit(limit, offset)
        return self

    def execute(self):
        return self.conn.execute(self.query, self.values)

    def __repr__(self):
        query_str = f"{self.query}" if getattr(self, "query", None) else ""
        values_str = f", {self.values}" if getattr(self, "values", None) else ""
        return f"{query_str}{values_str}"
