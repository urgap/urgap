"""UMeta subclass for using the sqlite interface."""

from __future__ import annotations

import sqlalchemy


from ._base import UMetaIOBase


class Base(DeclarativeBase):
    """SQLAlchemy base class."""





    )







class SQLAlchemyBaseUMeta(UMetaIOBase):
    """UMeta SQLAlchemy Base class."""

        self.name = "SQLAlchemyBaseUMeta"
        self._db = None

    @property
    def db(self) -> sqlalchemy.engine.Engine:
        if self._db is None:
            self._db = sqlalchemy.create_engine(self.generate_connection_string())
            Base.metadata.create_all(self._db)
        return self._db


        Args:
        """
        with Session(self.db) as session:
            )


        Args:
        """
        raise NotImplementedError(msg)


        with Session(self.db) as session:
            )


        Args:

        Returns:
        """
        with Session(self.db) as session:
            )


        Args:

        Returns:
        """
        return {
        }

        self,
        wid: str | None = None,
        limit: int | None = None,

        Args:
        """
        query = []
        if wid is not None:
        with Session(self.db) as session:
            if limit is not None:


        Args:
        """
        with Session(self.db) as session:
            session.commit()

        with Session(self.db) as session:
            )

    def generate_connection_string(self) -> None:
        msg = "Please implement this method in child classes."
        raise NotImplementedError(msg)