
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
        self._validate_share_name()


        self.conn_object.close()

    @property
        """Get remote file path.

        Returns:
        """
        return None

    @property
        """Get remote file tag path.

        Returns:
        """

        """Get remote tags associated with referenced file.

        Returns:
        """
        tags = None
        try:
            with BytesIO() as bio:
                bio.seek(0)
                file_content = bio.read()
                json_data = file_content.decode("utf-8")
                tags = json.loads(json_data)
        except OperationFailure:
            pass
        return tags

    def get_object(self) -> str:

        Returns:
        """
        return self.remote_path

        """Download referenced remote object.

        """

        if not self._remote_path_exists():
            self._create_fragment_directory()

        try:
        except (
            FileNotFoundError,
            IsADirectoryError,
            PermissionError,
            ValueError,
            OperationFailure,
            NotConnectedError,

            json_data = json.dumps(tags)
            json_bytes = json_data.encode("utf-8")
            with BytesIO(json_bytes) as bio:

    def remote_object_exists(self) -> bool:

        Returns:
        """
        try:
        except OperationFailure:
            return False

    def _remote_path_exists(self) -> bool:

        Returns:
        """
        try:
        except OperationFailure:
            return False

        smb_objects = []
        for obj in listed_objects:
            if obj.filename in (".", ".."):
                continue
            if obj.isDirectory is True:
                smb_objects.extend(
                )
            else:
                smb_objects.append(subpath + "/" + obj.filename)
        return smb_objects

    def list_container_items(
    ) -> list:
        """Get objects in folder/'container'.


        Args:
        Returns:
        """
        if pattern is not None:
            container_objects = [
                f for f in container_objects if re.search(pattern, f) is not None
            ]
        return container_objects


            try:
            except OperationFailure as e: