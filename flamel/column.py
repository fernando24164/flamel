from datetime import datetime


class Integer(int):
    type_name = "INTEGER"


class String(str):
    type_name = "TEXT"


class DateTime(datetime):
    type_name = "DATETIME"


class Real(float):
    type_name = "REAL"


class Blob(bytes):
    type_name = "BLOB"


class Boolean(int):
    type_name = "BOOLEAN"


class ForeignKey:
    """
    Represents a foreign key constraint in a database table.
    """

    def __init__(
        self, column_name: str, referenced_table: str, referenced_column: str
    ) -> None:
        """
        Initializes a new instance of the ForeignKey class with the specified properties.

        Args:
            column_name (str): The name of the column that is the foreign key.
            referenced_table (str): The name of the table that the foreign key references.
            referenced_column (str): The name of the column in the referenced table.
        """
        self.column_name = column_name
        self.referenced_table = referenced_table
        self.referenced_column = referenced_column

    def __repr__(self) -> str:
        return f"ForeignKey({self.column_name}, {self.referenced_table}, {self.referenced_column})"


class Column:
    """
    Represents a column in a database table.
    """

    def __init__(
        self,
        name: str,
        data_type: type,
        nullable: bool = True,
        default=None,
        primary_key: bool = False,
        unique: bool = False,
        check: str = None,
        autoincrement: bool = False,
        foreign_key: ForeignKey = None,
    ) -> None:
        """
        Initializes a new instance of the Column class with the specified properties.

        Args:
            name (str): The name of the column.
            data_type (type): The data type of the column.
            nullable (bool, optional): A boolean indicating if the column allows null values. Defaults to True.
            default (Any, optional): The default value for the column. Defaults to None.
            primary_key (bool, optional): A boolean indicating if the column is a primary key. Defaults to False.
            unique (bool, optional): A boolean indicating if the column values must be unique. Defaults to False.
            check (str, optional): A string representing a check constraint for the column. Defaults to None.
            autoincrement (bool, optional): A boolean indicating if the column has auto-incrementing values. Defaults to False.
            foreign_key (ForeignKey, optional): A ForeignKey object representing a foreign key constraint. Defaults to None.

        Raises:
            TypeError: If data_type is not a type.
            ValueError: If default value is not of the same type as data_type.
            TypeError: If check is not a string.
            TypeError: If foreign_key is not a ForeignKey object.
        """
        self.name = name
        if not isinstance(data_type, type) or not issubclass(
            data_type, (Integer, String, DateTime, Real, Blob, Boolean)
        ):
            raise TypeError("data_type must be a type")
        self.data_type = data_type
        self.nullable = nullable
        if default is not None:
            if issubclass(self.data_type, DateTime) and isinstance(default, str):
                self.default = f"'{default}'"
            elif hasattr(default, "__name__") and default.__name__ == "now":
                self.default = "CURRENT_TIMESTAMP"
            elif not issubclass(self.data_type, type(default)):
                raise ValueError("default value must be of the same type as data_type")
            else:
                self.default = default
        else:
            self.default = default
        self.primary_key = primary_key
        self.unique = unique
        if check is not None and not isinstance(check, str):
            raise TypeError("check must be a string")
        self.check = check
        self.autoincrement = autoincrement
        if foreign_key is not None and not isinstance(foreign_key, ForeignKey):
            raise TypeError("foreign_key must be a ForeignKey object")
        self.foreign_key = foreign_key

    def __repr__(self) -> str:
        attrs = [
            f"{key}={getattr(self, key)}" for key in self.__dict__ if key != "data_type"
        ]
        return f"Column({self.name}, {self.data_type.__name__}, {', '.join(attrs)})"
