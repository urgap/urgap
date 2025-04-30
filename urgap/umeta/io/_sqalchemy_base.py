"""UMeta subclass for using the sqlite interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import sqlalchemy

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    exists,
    func,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    aliased,
    mapped_column,
    relationship,
)

from ._base import UMetaIOBase

if TYPE_CHECKING:


class Base(DeclarativeBase):
    """SQLAlchemy base class."""


class ExecutionConfigurations(Base):
    __tablename__ = "umeta_execution_configurations"

    run_parameters: Mapped[dict[str, Any]] = mapped_column(JSON)
    command: Mapped[str] = mapped_column()
    unode: Mapped[str] = mapped_column()

    input_ufiles: Mapped[list[InputUFiles]] = relationship(
    )

    output_ufiles: Mapped[list[OutputUFiles]] = relationship(
    )


class InputUFiles(Base):
    __tablename__ = "umeta_input_ufiles"


    executions_as_input: Mapped[list[ExecutionConfigurations]] = relationship(
    )


class OutputUFiles(Base):
    __tablename__ = "umeta_output_ufiles"


    executions_as_output: Mapped[list[ExecutionConfigurations]] = relationship(
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
    user_dict: Mapped[UserDicts] = relationship(


class UserDicts(Base):
    __tablename__ = "user_dicts"

    data: Mapped[dict[str, str]] = mapped_column(JSON)
    execution_history: Mapped[ExecutionHistory] = relationship(
    )


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
            stmt = select(ExecutionConfigurations).where(
                exists(
                    select(1)
                    .select_from(input_link_alias)
                    .where(
                ),
            )
            results = session.execute(stmt).one_or_none()
            if not results:
                raise ValueError(msg)
            results = results[0]
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
            results = session.execute(statement).scalars().all()
            if not results:
                msg = "No ExecutionHistory entries found with given criteria"
                raise ValueError(msg)
            return {
                    "user_dict": result.user_dict.data if result.user_dict else None,
                    "started_time": result.started_time,
                    "duration_seconds": result.duration_seconds,
                }
                for result in results
            }

    def retrieve_interface_statistics(self) -> dict:
        with Session(self.db) as session:
            n_unode_exe_docs = select(func.count()).select_from(ExecutionConfigurations)
            n_uh_docs = select(func.count()).select_from(ExecutionHistory)
            n_input_links_docs = select(func.count()).select_from(ExecutionInputLink)
            n_output_links_docs = select(func.count()).select_from(ExecutionOutputLink)
            return {
                "Number of unode_exe_details Documents": session.execute(
                ).scalar(),
                "Number of input links Documents": session.execute(
                ).scalar(),
                "Number of output links Documents": session.execute(
                ).scalar(),
            }


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
            new_entry = ExecutionHistory(
                uwid=uwid,
                started_time=utrace.start_time,
                duration_seconds=utrace.duration_seconds,
            )
            session.add(new_entry)
            session.commit()

        with Session(self.db) as session:
            stmt = select(
            )
            return session.execute(stmt).scalar()


    def generate_connection_string(self) -> None:
        msg = "Please implement this method in child classes."
        raise NotImplementedError(msg)