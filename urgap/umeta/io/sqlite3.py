"""UMeta subclass for using the sqlite interface."""



    """UMeta sqlite class.

    SQlite is not intended for production use!
    """

        self._db = None
        self._session = None

        """Generate SQLAlchemy compatible connection string.

        Returns:
        """
        if sqlite3_url is None:
        return sqlite3_url