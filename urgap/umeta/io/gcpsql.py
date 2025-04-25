"""UMeta subclass for using the sqlite interface."""




class UMeta(SQLAlchemyBaseUMeta):
    """UMeta GCP Cloud SQL class."""

    def __init__(self) -> None:
        super().__init__()
        self._db = None
        self._session = None
        self.name = "UMeta GCP SQL"

    def generate_connection_string(self) -> str:

        Returns:
        """
        )
        )
        connection_string = (
            gcpsql_connection_string.replace(
            )
        )
        return connection_string.format(**credentials)