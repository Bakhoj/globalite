from dataclasses import dataclass
from .connection_manager import _ConnectionManager

def get_default_globalite() -> "_Globalite":
    return _Globalite("settings.db", "globals")


@dataclass
class _Globalite:
    def __init__(self, db_file: str, table_name: str):
        self.db_file = db_file
        self.table_name = table_name

        self._connection_manager = _ConnectionManager(self)

        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        pass