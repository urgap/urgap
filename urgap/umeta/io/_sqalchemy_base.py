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
    UniqueConstraint,
    desc,
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


class UcfsStorageLocation(Base):
    __tablename__ = "ucfs_storage_location"

    ucfs: Mapped[str] = mapped_column(primary_key=True)
    storage_base_uri: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (UniqueConstraint("ucfs", "storage_base_uri"),)


class ExecutionConfigurations(Base):
    __tablename__ = "umeta_execution_configurations"

    uunode_exe_id: Mapped[str] = mapped_column(primary_key=True)
    run_parameters: Mapped[dict[str, Any]] = mapped_column(JSON)
    command: Mapped[str] = mapped_column()
    unode: Mapped[str] = mapped_column()

    input_ufiles: Mapped[list[InputUFiles]] = relationship(
    )

    output_ufiles: Mapped[list[OutputUFiles]] = relationship(
    )


class InputUFiles(Base):
    __tablename__ = "umeta_input_ufiles"

    input_ucfs: Mapped[str] = mapped_column(primary_key=True)

    executions_as_input: Mapped[list[ExecutionConfigurations]] = relationship(
    )


class OutputUFiles(Base):
    __tablename__ = "umeta_output_ufiles"

    output_ucfs: Mapped[str] = mapped_column(
    )

    executions_as_output: Mapped[list[ExecutionConfigurations]] = relationship(
    )


class ExecutionInputLink(Base):
    __tablename__ = "execution_input_link"

    uunode_exe_id: Mapped[str] = mapped_column(
    )
    input_ucfs: Mapped[str] = mapped_column(
    )


class ExecutionOutputLink(Base):
    __tablename__ = "execution_output_link"

    uunode_exe_id: Mapped[str] = mapped_column(
    )
    output_ucfs: Mapped[str] = mapped_column(
    )


class ExecutionHistory(Base):
    __tablename__ = "umeta_execution_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    uunode_exe_id: Mapped[str] = mapped_column(index=True)
    uwid: Mapped[str] = mapped_column(index=True)
    started_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)

    user_dict: Mapped[UserDicts] = relationship(
    )


class UserDicts(Base):
    __tablename__ = "user_dicts"


    data: Mapped[dict[str, str]] = mapped_column(JSON)
    execution_history: Mapped[ExecutionHistory] = relationship(
    )


class SQLAlchemyBaseUMeta(UMetaIOBase):
    """UMeta SQLAlchemy Base class."""

    def __init__(self) -> None:
        """Create new UMeta object for use with sqlite3 interface."""
        self.name = "SQLAlchemyBaseUMeta"
        self._db = None
        super().__init__()

    @property
    def db(self) -> sqlalchemy.engine.Engine:
        """Return internal database object. Initializes database if none is available.

        Returns:
            SQLAlchemy engine object for the SQLite database.
        """
        if self._db is None:
            self._db = sqlalchemy.create_engine(self.generate_connection_string())
            Base.metadata.create_all(self._db)
        return self._db


        Args:

        Returns:
            Dictionary with node execution configuration details, including parameters,
            command, unode, input_ufiles, and output_ufiles.
        """
        with Session(self.db) as session:
            input_link_alias = aliased(ExecutionInputLink)
            stmt = select(ExecutionConfigurations).where(
                exists(
                    select(1)
                    .select_from(input_link_alias)
                    .where(
                        input_link_alias.uunode_exe_id
                ),
            )
            results = session.execute(stmt).one_or_none()
            if not results:
                raise ValueError(msg)
            results = results[0]
            input_ufile_list = [r.input_ucfs for r in results.input_ufiles]
            output_ufile_list = [r.output_ucfs for r in results.output_ufiles]
        return {
            "parameters": results.run_parameters,
            "command": results.command,
            "unode": results.unode,
            "input_ufiles": input_ufile_list,
            "output_ufiles": output_ufile_list,
        }


        Args:
        """
        msg = "Not yet implemented."
        raise NotImplementedError(msg)

        """Get the duration in seconds for a given execution.

        Args:
            uwid: Workflow ID.

        Returns:
            Float with duration in seconds, or None if not found.
        """
        with Session(self.db) as session:
            stmt = (
                select(ExecutionHistory.duration_seconds)
                .where(
                )
                .order_by(desc(ExecutionHistory.started_time))
                .limit(1)
            )
            return session.execute(stmt).scalar_one_or_none()


        Args:
            ucfs: UCFS string.

        Returns:
            List of node execution IDs that produced the UCFS.
        """
        with Session(self.db) as session:
            stmt = (
                select(ExecutionOutputLink.uunode_exe_id)
                .join(
                    OutputUFiles,
                    ExecutionOutputLink.output_ucfs == OutputUFiles.output_ucfs,
                )
                .filter(OutputUFiles.output_ucfs == ucfs)
            )
            return session.execute(stmt).scalars().all()


        Args:
            ucfs: UCFS string.

        Returns:
            List of node execution IDs that consumed the UCFS.
        """
        with Session(self.db) as session:
            stmt = (
                select(ExecutionOutputLink.uunode_exe_id)
                .join(
                    InputUFiles,
                    ExecutionInputLink.input_ucfs == InputUFiles.input_ucfs,
                )
                .filter(InputUFiles.input_ucfs == ucfs)
            )
            return session.execute(stmt).scalars().all()


        Args:
            ucfs: UCFS string.

        Returns:
            Dict with "consumers" and "producers" as lists of node execution IDs.
        """
        return {
        }

    def load_history(
        self,
        wid: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Load execution history from the database.

        Args:
            wid: Workflow ID to load the history for.
            limit: Optional maximum number of resulting history objects.

        Returns:
            Dictionary of execution history entries.
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
                (result.uunode_exe_id, result.uwid): {
                    "user_dict": result.user_dict.data if result.user_dict else None,
                    "started_time": result.started_time,
                    "duration_seconds": result.duration_seconds,
                }
                for result in results
            }

    def retrieve_interface_statistics(self) -> dict:
        """Count the number of UMeta entries available in the interface.

        Returns:
            Dictionary with counts of unode_exe_details, history, input links, and output links.
        """
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

        """Save UTrace information to the database.

        Args:
        """
        with Session(self.db) as session:
            if not self.umeta_exists(utrace=utrace):
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
        """Save input and output files to database and return lists of objects.

        Args:
            session: Active SQLAlchemy session.
            utrace: UTrace object.

        Returns:
            Tuple of lists: input_objs, output_objs
        """
        input_objs = []
        for ifile in utrace.input_files:
            obj = session.get(InputUFiles, ifile.ucfs)
            if not obj:
                obj = InputUFiles(input_ucfs=ifile.ucfs)
                session.add(obj)
            input_objs.append(obj)
        output_objs = []
        for ofile in utrace.output_files:
            if ofile is None:
                continue
            obj = session.get(OutputUFiles, ofile.ucfs)
            if not obj:
                obj = OutputUFiles(output_ucfs=ofile.ucfs)
                session.add(obj)
            output_objs.append(obj)
        return input_objs, output_objs

        """Save file information to UMeta.

        Args:
            ufile: UFile object.
        """
        with Session(self.db) as session:
            obj2 = UcfsStorageLocation(
                storage_base_uri=ufile.storage_base_uri,
                ucfs=ufile.ucfs,
            )
            try:
                session.add(obj2)
                session.flush()
                session.commit()
            except IntegrityError:
                session.rollback()

        """Check if UMeta (Unode execution details) exist for a given UTrace.

        Args:
            utrace: UTrace object.

        Returns:
            Boolean indicating if the configuration already exists.
        """
        with Session(self.db) as session:
            stmt = select(
            )
            return session.execute(stmt).scalar()

    def find_wid_members(self, wid: str, limit: int | None = None) -> dict:
        """Find all UMeta entries associated with a given workflow ID.

        Args:
            wid: Workflow ID.
            limit: Optional limit on number of entries.

        Returns:
            Dictionary of history entries.
        """
        return self.load_history(wid=wid, limit=limit)

    def generate_connection_string(self) -> None:
        """Generate a connection string for the database.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        msg = "Please implement this method in child classes."
        raise NotImplementedError(msg)

    def get_ucfs_object_name_info(
        self,
        storage_base_uri: str | None = None,
        object_name: str | None = None,
        ucfs: str | None = None,
    ) -> list[dict]:
        """Retrieve UMeta information for UCFS storage location.

        Args:
            storage_base_uri: Optional storage base UUri.
            object_name: Optional object name prefix.
            ucfs: Optional UCFS string.

        Returns:
            List of dictionaries with storage information.
        """
        stmt = select(UcfsStorageLocation.storage_base_uri, UcfsStorageLocation.ucfs)
        if storage_base_uri is not None:
            stmt = stmt.where(UcfsStorageLocation.storage_base_uri == storage_base_uri)
        if ucfs is not None:
            stmt = stmt.where(UcfsStorageLocation.ucfs == ucfs)
        if object_name is not None:
            stmt = stmt.where(UcfsStorageLocation.ucfs.like(f"{object_name}%"))
        with Session(self.db) as session:
            return session.execute(stmt).mappings().all()