import json
import logging
import re
from io import BytesIO



class IOSMB(UIOBase):

        """Create new UIO class for processing smb scheme.

        Args:
        """
        self.conn_object = SMBConnection(
            "Target",
            use_ntlm_v2=True,
            is_direct_tcp=True,
        )
        self.conn_object.connect(
        )
        self.conn_object.close()

        """Get remote tags associated with referenced file.

        Returns:
        """

    def get_object(self) -> str:

        Returns:
        """
        return self.remote_path

        """Download referenced remote object.

        """


    def remote_object_exists(self) -> bool:

        Returns:
        """
        try:
        except OperationFailure:
            return False

        """Get objects in folder/'container'.


        Args:
        Returns:
        """
        if pattern is not None:
            container_objects = [
            ]
