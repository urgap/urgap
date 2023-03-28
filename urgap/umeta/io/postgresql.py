"""UMeta subclass for using the sqlite interface."""



class UMeta(SQLAlchemyBaseUMeta):
    """UMeta postgresql class."""

        self._db = None
        self._session = None
        self.name = "UMeta postgresql"

        """Generate SQLAlchemy compatible connection string.

        Returns:
        """
        )
        )
        connection_string = postgresql_uri.replace(
        )
        return connection_string.format(**credentials)