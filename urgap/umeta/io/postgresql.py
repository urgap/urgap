"""UMeta subclass for using the sqlite interface."""

import urgap

from urgap.umeta.io._sqalchemy_base import SQLAlchemyBaseUMeta


class UMeta(SQLAlchemyBaseUMeta):
    """UMeta postgresql class."""

    def __init__(self) -> None:
        """Create new UMeta object using postgresql."""
        super().__init__()
        self._db = None
        self._session = None
        self.name = "UMeta postgresql"

    def generate_connection_string(self) -> str:
        """Generate SQLAlchemy compatible connection string.

        Returns:
            Connection string.
        """
        postgresql_uri = urgap.config.get(
            "umeta-postgresql-url",
            "postgresql://localhost:5432",
        )
        credentials = urgap.instances.ucredential_manager.extract_credentials(
            postgresql_uri,
        )
        connection_string = postgresql_uri.replace(
            "postgresql://",
            "postgresql://{user}:{password}@",
        )
        return connection_string.format(**credentials)