"""UMeta subclass for using the sqlite interface."""



class UMeta(SQLAlchemyBaseUMeta):
    """UMeta postgresql class."""

        self._db = None
        self._session = None
        self.name = "UMeta postgresql"

    def generate_connection_string(self) -> str:
        """Generate SQLAlchemy compatible connection string.

        Returns:
            Connection string.
        """
        )
        )
        connection_string = postgresql_uri.replace(
        )
        return connection_string.format(**credentials)