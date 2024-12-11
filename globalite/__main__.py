from dataclasses import dataclass
from .connection_manager import _ConnectionManager
import os
import json

_ignored_variable_names = [
    "db_file",
    "table_name",
    "_conn",
    "_cursor",
    "_connection_manager",
    "_globalite_dicts"
]


def get_default_globalite() -> "_Globalite":
    return _Globalite("settings.db", "globals")


@dataclass
class _Globalite:
    def __init__(self, db_file: str, table_name: str):
        self.db_file = db_file
        self.table_name = table_name
        self._globalite_dicts = dict()

        self._connection_manager = _ConnectionManager(self)

        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        with self.get_connection() as (conn, cursor):
            if self._has_table(cursor):
                return
            
            query = f"CREATE TABLE IF NOT EXISTS {self.table_name} (key TEXT, value TEXT, type TEXT, PRIMARY KEY (key))"

            cursor.execute(query)
            conn.commit()

    def _has_table(self, cursor) -> bool:
        query = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?"
        cursor.execute(query, (self.table_name,))

        return cursor.fetchone()[0] > 0

    def get_connection(self) -> "_ConnectionManager":
        return self._connection_manager
    
    def __setattr__(self, __name: str, __value) -> None:
        if __name in _ignored_variable_names:
            super().__setattr__(__name, __value)
        else:
            with self.get_connection() as (conn, cursor):
                query = f"INSERT OR REPLACE INTO {self.table_name} (key, value, type) VALUES(?, ?, ?)"
                if type(__value) is dict:
                    cursor.execute(query, (__name, json.dumps(__value), str(type(__value).__name__)))
                else:
                    cursor.execute(query, (__name, __value, str(type(__value).__name__)))
                conn.commit()

    def __getattr__(self, __name: str) -> None:
        if __name in _ignored_variable_names:
            return super().__getattr__(__name)
        with self.get_connection() as (conn, cursor):
            query = f"SELECT value, type FROM {self.table_name} WHERE key = ?"
            cursor.execute(query, (__name,))
            result = cursor.fetchone()
            if result is None:
                raise AttributeError(f"'{self.__class__.__name__}' has no object '{__name}'")
            _type = result[1]
            if _type == "dict":
                return json.loads(result[0])
            if _type == "int":
                return int(result[0])
            if _type == "bool":
                return bool(int(result[0]))
            if _type == "float":
                return float(result[0])
            if _type == "str" or _type =="NoneType":
                return result[0]
            raise ValueError(f"Unsupported value type '{_type}' for key '{__name}' value '{result[0]}'")

    def __delattr__(self, __name: str) -> None:
        if __name in _ignored_variable_names:
            super().__delattr__(__name)
        else:
            with self.get_connection() as (conn, cursor):
                query = f"DELETE FROM {self.table_name} WHERE key = ?"
                cursor.execute(query, (__name,))
                conn.commit()

    def keys(self) -> set:
        keys: set[str] = set()
        with self.get_connection() as (conn, cursor):
            query = f"SELECT key FROM {self.table_name}"
            cursor.execute(query)
            for item in cursor.fetchall():
                keys.add(item[0])
        return keys
