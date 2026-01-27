"""UMeta subclass for using the sqlite interface."""

import urgap

from urgap.umeta.io._sqalchemy_base import SQLAlchemyBaseUMeta


class UMeta(SQLAlchemyBaseUMeta):
    """UMeta GCP Cloud SQL class."""

    def __init__(self) -> None:
        """Create new UMeta object using GCP Cloud SQL."""
        super().__init__()
        self._db = None
        self._session = None
        self.name = "UMeta GCP SQL"

    def generate_connection_string(self) -> str:
        """Generate SQLAlchemy-compatible connection string.

        Returns:
            Connection string for SQLAlchemy to connect to the GCP Cloud SQL instance.
        """
        gcpsql_connection_string = urgap.config.get(
            "umeta-gcpsql-url",
            "postgresql+pg8000://10.0.0.0:5432",
        )
        credentials = urgap.instances.ucredential_manager.extract_credentials(
            gcpsql_connection_string,
        )
        connection_string = (
            gcpsql_connection_string.replace(
                "postgresql+pg8000://",
                "postgresql+pg8000://{user}:{password}@",
            )
            + "/urgap"
        )
        return connection_string.format(**credentials)
