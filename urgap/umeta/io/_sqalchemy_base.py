"""UMeta subclass for using the sqlite interface."""
import sqlalchemy


    )


    """UMeta SQLAlchemy Base class."""

        self._db = None

    @property
        if self._db is None:
            self._db = sqlalchemy.create_engine(self.generate_connection_string())
        return self._db

        with Session(self.db) as session: