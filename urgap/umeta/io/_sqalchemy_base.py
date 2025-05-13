"""UMeta subclass for using the sqlite interface."""

from __future__ import annotations

import logging

from typing import TYPE_CHECKING, Any

import sqlalchemy

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    exists,
    func,
    select,
)
from sqlalchemy.exc import IntegrityError
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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    uwid: Mapped[str] = mapped_column(index=True)
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
            stmt = (
                select(ExecutionHistory.duration_seconds)
                .where(
                )
                .order_by(desc(ExecutionHistory.started_time))
                .limit(1)
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

    def load_history(
        self,
        wid: str | None = None,
        limit: int | None = None,
    ) -> dict:

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
                "Number of history Documents": session.execute(n_uh_docs).scalar(),
                "Number of input links Documents": session.execute(
                ).scalar(),
                "Number of output links Documents": session.execute(
                ).scalar(),
            }


        Args:
        """
        with Session(self.db) as session:
                input_objs, output_objs = self._save_input_and_output_files(
                )
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

    def _save_input_and_output_files(
    ) -> tuple[list, list]:
        input_objs = []
        for ifile in utrace.input_files:
            obj = session.get(InputUFiles, ifile.ucfs)
            if not obj:
                session.add(obj)
            input_objs.append(obj)
        output_objs = []
        for ofile in utrace.output_files:
            if ofile is None:
                continue
            obj = session.get(OutputUFiles, ofile.ucfs)
            if not obj:
                session.add(obj)
            output_objs.append(obj)
        return input_objs, output_objs

        with Session(self.db) as session:
                storage_base_uri=ufile.storage_base_uri,
            )
            try:
                session.add(obj2)
                session.flush()
                session.commit()
            except IntegrityError:
                session.rollback()

        with Session(self.db) as session:
            stmt = select(
            )
            return session.execute(stmt).scalar()

    def find_wid_members(self, wid: str, limit: int | None = None) -> dict:
        return self.load_history(wid=wid, limit=limit)

    def generate_connection_string(self) -> None:
        msg = "Please implement this method in child classes."
        raise NotImplementedError(msg)

    def get_ucfs_object_name_info(
        self,
        storage_base_uri: str | None = None,
        object_name: str | None = None,
    ) -> list[dict]:
        if storage_base_uri is not None:
        if object_name is not None:
        with Session(self.db) as session:
            return session.execute(stmt).mappings().all()