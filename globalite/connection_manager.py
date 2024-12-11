import sqlite3
from typing import Optional

class _ConnectionManager:

    def __init__(self, globalite: "_Globalite"):
        self._globalite: "_Globalite" = globalite
        self._conn: Optional[sqlite3.Connection] = None

    def __enter__(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        self._conn = sqlite3.connect(self._globalite.db_file)
        return self._conn, self._conn.cursor()
    
    def __exit__(self, *_):
        self._conn.close()
