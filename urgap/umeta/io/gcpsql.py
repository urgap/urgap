"""UMeta subclass for using the sqlite interface."""


class UMeta(SQLAlchemyBaseUMeta):
    """UMeta GCP Cloud SQL class."""

        self._db = None
        self._session = None


        Returns:
        """
        )
        )
        connection_string = (
            gcpsql_connection_string.replace(
            )
        )
        return connection_string.format(**credentials)