"""UMeta subclass for using the sqlite interface."""
import sqlalchemy
from ._base import UMetaIOBase



    )







    """UMeta SQLAlchemy Base class."""

        self._db = None

    @property
        if self._db is None:
            self._db = sqlalchemy.create_engine(self.generate_connection_string())
        return self._db


        Args:
        """
        with Session(self.db) as session:
            )


        Args:
        """


        Args:
        """
        query = []
        if wid is not None:
        with Session(self.db) as session:


        Args:
        """
        with Session(self.db) as session:
            session.commit()

        with Session(self.db) as session: