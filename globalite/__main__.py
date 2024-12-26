from dataclasses import dataclass
from .connection_manager import _ConnectionManager
import os
import json


# private variables is prefixed with "_gl_"
_ignored_variable_names = [
    "_gl_db_file",
    "_gl_table_name",
    "_gl_connection_manager",
]


def get_default_globalite() -> "_Globalite":
    return _Globalite("settings.db", "globals")


@dataclass
class _Globalite:
    def __init__(self, db_file: str, table_name: str):
        self._gl_db_file = db_file
        self._gl_table_name = table_name

        self._gl_connection_manager = _ConnectionManager(self)

        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        with self.get_connection() as (conn, cursor):
            if self._has_table(cursor):
                return

            query = f"CREATE TABLE IF NOT EXISTS {self._gl_table_name} (key TEXT, value TEXT, type TEXT, PRIMARY KEY (key))"

            cursor.execute(query)
            conn.commit()

    def _has_table(self, cursor) -> bool:
        query = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?"
        cursor.execute(query, (self._gl_table_name,))

        return cursor.fetchone()[0] > 0

    def get_connection(self) -> "_ConnectionManager":
        return self._gl_connection_manager

    def __setattr__(self, __name: str, __value) -> None:
        if __name in _ignored_variable_names:
            super().__setattr__(__name, __value)
        else:
            with self.get_connection() as (conn, cursor):
                query = f"INSERT OR REPLACE INTO {self._gl_table_name} (key, value, type) VALUES(?, ?, ?)"
                if type(__value) is dict:
                    cursor.execute(query, (__name, json.dumps(__value), str(type(__value).__name__)))
                else:
                    cursor.execute(query, (__name, __value, str(type(__value).__name__)))
                conn.commit()

    def __getattr__(self, __name: str) -> None:
        if __name in _ignored_variable_names:
            return super().__getattr__(__name)
        with self.get_connection() as (conn, cursor):
            query = f"SELECT value, type FROM {self._gl_table_name} WHERE key = ?"
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
                query = f"DELETE FROM {self._gl_table_name} WHERE key = ?"
                cursor.execute(query, (__name,))
                conn.commit()

    def keys(self) -> set:
        keys: set[str] = set()
        with self.get_connection() as (conn, cursor):
            query = f"SELECT key FROM {self._gl_table_name}"
            cursor.execute(query)
            for item in cursor.fetchall():
                keys.add(item[0])
        return keys

    def flush_database(self) -> None:
        '''
            Will flush the database file, meaning it will do the fsync system call
            that makes sure the database file is written to disk.

            OBS use with caution and only when a value is at risk of being forgotten by
            a soon thereafter power outage. The operation is more expensive, performance-wise,
            than normal save.

            The OS does these for the full system regularly so it is only needed in rare occasions.

            https://www.tutorialspoint.com/python/os_fsync.htm
            https://www.sqlite.org/atomiccommit.html (9.2 Incomplete Disk Flushes)
        '''
        with open(self._gl_db_file) as f:
            os.fsync(f)
