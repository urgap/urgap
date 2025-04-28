"""UMeta subclass for using the sqlite interface."""

from __future__ import annotations

import sqlalchemy

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    aliased,
    mapped_column,
    relationship,
)

from ._base import UMetaIOBase


class Base(DeclarativeBase):
    """SQLAlchemy base class."""


class ExecutionConfigurations(Base):
    __tablename__ = "umeta_execution_configurations"

    command: Mapped[str] = mapped_column()
    unode: Mapped[str] = mapped_column()

    )

    )


class InputUFiles(Base):
    __tablename__ = "umeta_input_ufiles"


    )


class OutputUFiles(Base):
    __tablename__ = "umeta_output_ufiles"


    )


class ExecutionInputLink(Base):
    __tablename__ = "execution_input_link"

    )
    )


class ExecutionOutputLink(Base):
    __tablename__ = "execution_output_link"

    )
    )


class ExecutionHistory(Base):
    __tablename__ = "umeta_execution_history"

    started_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)


class UserDicts(Base):
    __tablename__ = "user_dicts"


class SQLAlchemyBaseUMeta(UMetaIOBase):
    """UMeta SQLAlchemy Base class."""

    def __init__(self) -> None:
        self.name = "SQLAlchemyBaseUMeta"
        self._db = None
        super().__init__()

    @property
    def db(self) -> sqlalchemy.engine.Engine:
        if self._db is None:
            self._db = sqlalchemy.create_engine(self.generate_connection_string())
            Base.metadata.create_all(self._db)
        return self._db


        Args:
        """
        with Session(self.db) as session:
            input_link_alias = aliased(ExecutionInputLink)
            )
            results = session.execute(stmt).one_or_none()
            if not results:
        return {
            "parameters": results.run_parameters,
            "command": results.command,
            "unode": results.unode,
            "input_ufiles": input_ufile_list,
            "output_ufiles": output_ufile_list,
        }


        Args:
        """
        raise NotImplementedError(msg)

        with Session(self.db) as session:
            )
            return session.execute(stmt).scalar_one_or_none()

        with Session(self.db) as session:
            stmt = (
                .join(
                    OutputUFiles,
                )
            )
            return session.execute(stmt).scalars().all()


        Args:

        Returns:
        """
        with Session(self.db) as session:
            stmt = (
                .join(
                    InputUFiles,
                )
            )
            return session.execute(stmt).scalars().all()


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
            query.append(ExecutionHistory.uwid == wid)
        with Session(self.db) as session:
            statement = select(ExecutionHistory).filter(*query)
            if limit is not None:
                statement = statement.limit(limit)


        Args:
        """
        with Session(self.db) as session:
                session.flush()
                new_config = ExecutionConfigurations(
                    run_parameters=utrace.urun_dict.parameters,
                    command="".join(utrace.urun_dict.command_list),
                    unode=utrace.unode_meta["unode_full_identifier"],
                    input_ufiles=input_objs,
                    output_ufiles=output_objs,
                )
                session.add(new_config)
            session.commit()

        with Session(self.db) as session:
            stmt = select(
            )
            return session.execute(stmt).scalar()


    def generate_connection_string(self) -> None:
        msg = "Please implement this method in child classes."
        raise NotImplementedError(msg)