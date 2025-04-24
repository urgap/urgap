
import json
import logging
import re

from io import BytesIO
from pathlib import Path

from smb.base import NotConnectedError, SMBTimeout
from smb.smb_structs import OperationFailure
from smb.SMBConnection import SMBConnection



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

    def _validate_share_name(self) -> None:
            raise ValueError(msg)

    def __del__(self) -> None:
        self.conn_object.close()

    @property
    def remote_path(self) -> str | None:
        """Get remote file path.

        Returns:
        """
        return None

    @property
    def remote_tag_path(self) -> str | None:
        """Get remote file tag path.

        Returns:
        """

    def get_remote_tags(self) -> dict | None:
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

    def download(self) -> None:
        """Download referenced remote object.

        """
        try:
            self.scratch_path.unlink(missing_ok=True)

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
            msg = f"Could not copy file {self.scratch_path}"

            json_data = json.dumps(tags)
            json_bytes = json_data.encode("utf-8")
            with BytesIO(json_bytes) as bio:

    def remote_object_exists(self) -> bool:

        Returns:
        """
        try:
            return any(f.filename == filename for f in files)
        except OperationFailure:
            return False

    def _remote_path_exists(self) -> bool:

        Returns:
        """
        try:
        except OperationFailure:
            return False
        else:
            return True

    def _get_files_recursively(self, subpath: str | Path) -> list:
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

    def _create_fragment_directory(self) -> None:

        for level, _directory in enumerate(fragment_dirs):
            path_to_create = "/".join(fragment_dirs[: level + 1])
            try:
            except OperationFailure as e:
                msg = f"Could not create folder {path_to_create} with {e}"