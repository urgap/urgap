
import logging



class UMeta:

    This interface is used to track run information based on UTraces.


    """


        Args:
        """
        self._io = None
        if io is None:
        self._io_id = io


        Args:
        """
        urd.command_list = node_exe_details["command"].split(" ")
        urd["wid"] = wid  # not using urd.wid to avoid the warning :)
            urun_dict=urd,
        )


        Args:
        """


        Args:
        """

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


        Args:
        """

    def find_last_processed_files(self, unode: str, last: int = 10) -> list:

        Args:

        Returns:
            List of node_exe_details sorted from newest to oldest.
        """
        return self.io.find_last_processed_files(unode, last=last)


        Args:

        Returns:
        """