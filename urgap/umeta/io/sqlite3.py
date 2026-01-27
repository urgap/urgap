"""UMeta subclass for using the sqlite interface."""

import urgap

from urgap.umeta.io._sqalchemy_base import SQLAlchemyBaseUMeta


class UMeta(SQLAlchemyBaseUMeta):
    """UMeta sqlite class.

    SQlite is not intended for production use!
    """

    def __init__(self) -> None:
        """Create new UMeta object for use with sqlite3 interface."""
        super().__init__()
        self._db = None
        self._session = None
        self.name = "UMeta sqlite3"

    def generate_connection_string(self) -> str:
        """Generate SQLAlchemy compatible connection string.

        Returns:
            Connection string.
        """
        sqlite3_url = urgap.config.get("umeta-sqlite3-url", None)
        if sqlite3_url is None:
            sqlite3_url = f"sqlite:///{urgap.home}/umeta_sqlite.db"
        return sqlite3_url
