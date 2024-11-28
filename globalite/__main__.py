from dataclasses import dataclass
from typing import Optional
import sqlite3

def get_default_globalite() -> "_Globalite":
    return _Globalite("settings.db", "globals")

class _ConnectionManager:

    def __init__(self, glob: "_Globalite"):
        self._glob: _Globalite = glob
        self._conn: Optional[sqlite3.Connection] = None

    def __enter__(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        self._conn = sqlite3.connect(self._glob.db_file)
        return self._conn, self._conn.cursor()
    
    def __exit__(self, *_):
        self._conn.close()

@dataclass
class _Globalite:
    def __init__(self, db_file: str, table_name: str):
        self.db_file = db_file
        self.table_name = table_name

        self._connection_manager = _ConnectionManager(self)

        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        pass