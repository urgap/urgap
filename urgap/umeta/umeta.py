"""UFile module of urgap2."""

from __future__ import annotations

import logging

import urgap

logger = logging.getLogger(__name__)


class UMeta:
    """Urgap UMeta interface.

    This interface is used to track run information based on UTraces.

    It manages three collections/tables in the IO interfaces defined in `urgap.json`
    or passed via the `io` argument.

    Notes:
        1. **UNode execution details:** The primary key is based on unode_meta + parameters + filestem,
           as defined by UTrace.determine_output_files_stem().
        2. **History:** Primary key is (1) + wid.
        3. **Links:** UFile <-> UNode association, with columns: primary key (from 1), source, and target.
            - {source: input_file, target: UNode, pac_id: 1._id }
            - {source: UNode, target: output_file, pac_id: 1._id }
    """

    def __init__(self, io: str | None = None) -> None:
        """Initialize UMeta Interface.

        Args:
            io: UMeta interface to use. Options are in `urgap.umeta.io`.
                Defaults to None, which uses the interface specified in `$URGAP_HOME/urgap.config`.
        """
        self._io = None
        if io is None:
            io = urgap.config.get("umeta", "dummy")
        self._io_id = io

    @property
    def io(self) -> urgap.UMeta:
        """IO Property, enabling on-demand initialization of the IO class.

        Notes:
            - The IO backend cannot be serialized.
            - This property allows deleting `_io` safely, as it will be re-initialized when accessed.

        Returns:
            Initialized Urgap IO class.
        """
        if self._io is None:
            self._io = self.init_io_class()
        return self._io

    def init_io_class(self) -> urgap.UMeta:
        """Initialize the appropriate IO class for UMeta.

        Raises:
            ModuleNotFoundError: If the selected `io` backend is not supported.

        Returns:
            Initialized IO class for UMeta operations.
        """
        available_ios = {
            "postgresql": urgap.umeta.io.postgresql.UMeta,
            "sqlite3": urgap.umeta.io.sqlite3.UMeta,
            "gcpsql": urgap.umeta.io.gcpsql.UMeta,
        }

        if self._io_id in available_ios:
            io = available_ios[self._io_id]()
        else:
            msg = (
                f"Cannot initialize driver for unknown IO type '{self._io_id}'. "
                f"Currently supported: {list(available_ios.keys())}"
            )
            raise ModuleNotFoundError(msg)
        return io

    def umeta_exists(self) -> bool:
        """Check if UMeta metadata exists for a given reference file.

        Returns:
            True if UMeta metadata exists.
        """
        return self.io.umeta_exists(self)

    def save_utrace(self, utrace: urgap.UTrace) -> None:
        """Save a UTrace object using the IO backend.

        Args:
            utrace: UTrace object to save.
        """
        self.io.save(utrace)

    def load_utrace(
        self,
        pac_id: str,
        wid: str,
        storage_base_uri: str,
        history: dict | None = None,
    ) -> urgap.UTrace:
        """Load a UTrace object using the IO backend.

        Args:
            pac_id: Node execution ID to load the UTrace for.
            wid: Workflow ID (WID) to load the UTrace for.
            history: If provided, load history for the given pac_id and wid.
            storage_base_uri: Storage base UUri for referenced UFiles.

        Returns:
            Loaded UTrace object.
        """
        node_exe_details = self.load_node_exe_details(pac_id)
        if history is None:
            history = self.load_history(pac_id=pac_id, wid=wid)
        if ":" in pac_id:
            urd = urgap.URunDict(
                {
                    "parameters": node_exe_details["parameters"],
                    "user_dict": {
                        "!NOTE!": "User dicts can be modified from run to run and"
                        " from node to node.",
                    },
                },
            )
            _, unode_version = node_exe_details["unode"].split(":")
        else:
            urd = urgap.URunDict(
                {
                    "parameters": node_exe_details["parameters"],
                    "user_dict": {
                        "!NOTE!": "User dicts can be modified from run to run and"
                        " from node to node.",
                    },
                },
            )
            unode_version = None
        urd.command_list = node_exe_details["command"].split(" ")
        urd["wid"] = wid  # not using urd.wid to avoid the warning :)
        return urgap.UTrace(
            urun_dict=urd,
            input_files=urgap.UFileList(
                [
                    urgap.UFile(uri=f"{storage_base_uri}#{ucfs}")
                    for ucfs in node_exe_details["input_ufiles"]
                ],
            ),
            unode_meta=urgap.init_unode(node_exe_details["unode"]).META_INFO,
            unode_version=unode_version,
            output_files=urgap.UFileList(
                [
                    urgap.UFile(uri=f"{storage_base_uri}#{ucfs}")
                    for ucfs in node_exe_details["output_ufiles"]
                ],
            ),
            history=history,
        )

    def load_node_exe_details(self, pac_id: str) -> urgap.UTrace:
        """Load details for a given node execution ID.

        Args:
            pac_id: Node execution ID to load details for.

        Returns:
            Node execution details object.
        """
        return self.io.load_node_exe_details(pac_id)

    def load_history(
        self,
        pac_id: str | None = None,
        wid: str | None = None,
    ) -> dict:
        """Load execution history using the IO backend.

        Args:
            pac_id: Node execution ID to load history for.
            wid: Workflow ID to load history for.

        Returns:
            Loaded execution history.

        Raises:
            OSError: If both pac_id and wid are None.
        """
        if pac_id is None and wid is None:
            logger.warning("Will NOT extract complete UMeta DB! Use a DB browser ...")
            raise OSError
        return self.io.load_history(pac_id=pac_id, wid=wid)

    def delete(self, reference_ufile: urgap.UFile) -> None:
        """Delete UMeta entries for a given reference file.

        Args:
            reference_ufile: UFile whose UMeta entry should be deleted.
        """
        self.io.delete(reference_ufile)

    def find_pac_ids(self, ucfs: str) -> list:
        """Find all pac_id values for a given object name.

        Args:
            ucfs: Object name to query.

        Returns:
            List of pac_ids.
        """
        return self.io.find_pac_ids(ucfs)

    def find_pac_ids_of_producers(self, ucfs: str) -> list:
        """Find all producer pac_ids for a given object name.

        Args:
            ucfs: Object name to query.

        Returns:
            List of pac_ids that produced the object.
        """
        return self.io.find_pac_ids_of_producers(ucfs)

    def find_pac_ids_of_consumers(self, ucfs: str) -> list:
        """Find all consumer pac_ids for a given object name.

        Args:
            ucfs: Object name to query.

        Returns:
            List of pac_ids that consumed the object.
        """
        return self.io.find_pac_ids_of_consumers(ucfs)

    def retrieve_interface_statistics(self) -> dict:
        """Retrieve statistics from the UMeta IO interface.

        Returns:
            Dictionary of statistics for the backend interface.
        """
        return self.io.retrieve_interface_statistics()

    def find_wid_members(self, wid: str, limit: int | None = None) -> dict:
        """Load history for a given workflow ID (wid).

        Args:
            wid: Urgap workflow ID.
            limit: Maximum number of resulting history objects.

        Returns:
            History records for the given wid.
        """
        return self.io.find_wid_members(wid=wid, limit=limit)

    def find_last_processed_files(self, unode: str, last: int = 10) -> list:
        """Retrieve the last N output files for a given UNode.

        Args:
            unode: UNode identifier.
            last: Number of last entries to return (default 10).

        Returns:
            List of node_exe_details sorted from newest to oldest.
        """
        return self.io.find_last_processed_files(unode, last=last)

    def find_pac_id_details(self, pac_id: str) -> list:
        """Find details for a given pac_id.

        Args:
            pac_id: Node execution ID.

        Returns:
            Details for the given pac_id.
        """
        return self.io.find_pac_id_details(pac_id)

    def save_rebased_file_to_ucfs_storage_location(self, ufile: urgap.UFile) -> None:
        """Save rebased file information to UMeta.

        Args:
            ufile: UFile to update in UMeta.
        """
        self.io.save_rebased_file_to_ucfs_storage_location(ufile=ufile)

    def get_ucfs_object_name_info(
        self,
        storage_base_uri: str | None = None,
        object_name: str | None = None,
        ucfs: str | None = None,
    ) -> list[dict]:
        """Retrieve UMeta information for a given ucfs storage location.

        Args:
            storage_base_uri: Storage base UUri.
            object_name: Object name.
            ucfs: UCFS string.

        Returns:
            List of dictionaries with UMeta information for the specified query.
        """
        self.io.get_ucfs_object_name_info(
            storage_base_uri=storage_base_uri,
            object_name=object_name,
            ucfs=ucfs,
        )