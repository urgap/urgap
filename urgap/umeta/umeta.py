
from __future__ import annotations

import logging



class UMeta:

    This interface is used to track run information based on UTraces.


    """

    def __init__(self, io: str | None = None) -> None:

        Args:
        """
        self._io = None
        if io is None:
        self._io_id = io

    def load_utrace(
        self,
        wid: str,
        history: dict | None = None,

        Args:
        """
        if history is None:
                {
                    "parameters": node_exe_details["parameters"],
                    "user_dict": {
                        "!NOTE!": "User dicts can be modified from run to run and"
                    },
            )
            _, unode_version = node_exe_details["unode"].split(":")
        else:
                {
                    "parameters": node_exe_details["parameters"],
                    "user_dict": {
                        "!NOTE!": "User dicts can be modified from run to run and"
                    },
            )
            unode_version = None
        urd.command_list = node_exe_details["command"].split(" ")
        urd["wid"] = wid  # not using urd.wid to avoid the warning :)
            urun_dict=urd,
                [
                    for ucfs in node_exe_details["input_ufiles"]
            ),
            unode_version=unode_version,
                [
                    for ucfs in node_exe_details["output_ufiles"]
            ),
            history=history,
        )


        Args:
        """

    def load_history(
    ) -> dict:

        Args:
        """
            raise OSError

        """Delete UMeta entries for a given reference file.

        Args:
        """
        self.io.delete(reference_ufile)


        Args:

        Returns:
        """


        Args:

        Returns:
        """


        Args:

        Returns:
        """

    def retrieve_interface_statistics(self) -> dict:
        return self.io.retrieve_interface_statistics()

    def find_wid_members(self, wid: str, limit: int | None = None) -> dict:

        Args:
            limit: Maximum number of resulting history objects.
        """
        return self.io.find_wid_members(wid=wid, limit=limit)

    def find_last_processed_files(self, unode: str, last: int = 10) -> list:

        Args:

        Returns:
            List of node_exe_details sorted from newest to oldest.
        """
        return self.io.find_last_processed_files(unode, last=last)


        Args:

        Returns:
        """

        self.io.save_rebased_file_to_ucfs_storage_location(ufile=ufile)

    def get_ucfs_object_name_info(
        self,
        storage_base_uri: str | None = None,
        object_name: str | None = None,
        ucfs: str | None = None,
    ) -> list[dict]:
        self.io.get_ucfs_object_name_info(
        )