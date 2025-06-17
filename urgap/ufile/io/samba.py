
import json
import logging
import re

from io import BytesIO
from pathlib import Path
from typing import ParamSpec

from smb.base import NotConnectedError, SMBTimeout
from smb.smb_structs import OperationFailure
from smb.SMBConnection import SMBConnection


P = ParamSpec("P")


class IOSMB(UIOBase):
    """UIO Class interface for SMB (Samba) file objects.

    Handles interaction with remote SMB shares for reading, writing, and listing files and metadata.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new UIO class for processing smb scheme.

        Args:
            **kwargs: Requires 'uuri' key to set respective attributes.
                Example uri: smb://10.0.20.165:445/<share, e.g. MyShare>#<path_on_share_to_file>
        """
        super().__init__(**kwargs)
        self.conn_object = SMBConnection(
            self.uuri.query,
            self.uuri.password,
            "Target",
            use_ntlm_v2=True,
            is_direct_tcp=True,
        )
        self.conn_object.connect(
            self.uuri.get_host(),
            self.uuri.get_port(),
        )
        self._validate_share_name()

    def _validate_share_name(self) -> None:
        """Check if share name contains forbidden character '/'.

        Raises:
            ValueError if '/' is present in the share name.
        """
        if "/" in self.uuri.get_samba_share():
            msg = f"Share name '{self.uuri.get_samba_share()}' contains invalid character '/'."
            raise ValueError(msg)

    def __del__(self) -> None:
        """Close SMB connection on object deletion."""
        self.conn_object.close()

    @property
    def remote_path(self) -> str | None:
        """Get remote file path.

        Returns:
            None (handled by SMB API).
        """
        return None

    @property
    def remote_tag_path(self) -> str | None:
        """Get remote file tag path.

        Returns:
            String representing the remote tag file path.
        """
        return self.uuri.fragment + ".tag"

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with referenced file.

        Returns:
            Dictionary of remote tags if found, otherwise None.
        """
        tags = None
        try:
            with BytesIO() as bio:
                self.conn_object.retrieveFile(
                    self.uuri.get_samba_share(),
                    self.remote_tag_path,
                    bio,
                )
                bio.seek(0)
                file_content = bio.read()
                json_data = file_content.decode("utf-8")
                tags = json.loads(json_data)
        except OperationFailure:
            pass
        return tags

    def get_object(self) -> str:
        """Get referenced UUri.

        Returns:
            Remote UUri (for SMB, handled by the internal API).
        """
        return self.remote_path

    def download(self) -> None:
        """Download referenced remote object.

        Writes the remote SMB file to the local scratch path.

        Raises:
            RuntimeError: If a SMBTimeout occurs during file retrieval.
        """
        try:
            with self.scratch_path.open("wb") as ooo:
                self.conn_object.retrieveFile(
                    self.uuri.get_samba_share(),
                    self.uuri.fragment,
                    ooo,
                )
        except SMBTimeout as e:
            self.scratch_path.unlink(missing_ok=True)
            raise RuntimeError from e

    def upload(self, tags: dict | None = None) -> None:
        """Upload files and tags to the SMB share.

        Args:
            tags: Dictionary of tags to upload as a .tag file with the same name.
        """
        if not self._remote_path_exists():
            self._create_fragment_directory()

        try:
            with self.scratch_path.open("rb") as ooo:
                self.conn_object.storeFile(
                    self.uuri.get_samba_share(),
                    self.uuri.fragment,
                    ooo,
                )
        except (
            FileNotFoundError,
            IsADirectoryError,
            PermissionError,
            ValueError,
            OperationFailure,
            NotConnectedError,
        ) as e:
            msg = f"Could not copy file {self.scratch_path}"
            raise RuntimeError(msg) from e

        if tags is None:
        else:
            json_data = json.dumps(tags)
            json_bytes = json_data.encode("utf-8")
            with BytesIO(json_bytes) as bio:
                self.conn_object.storeFile(
                    self.uuri.get_samba_share(),
                    self.remote_tag_path,
                    bio,
                )

    def remote_object_exists(self) -> bool:
        """Verify if the referenced remote object exists.

        Returns:
            True if remote object exists, False otherwise.
        """
        try:
            fragment_directory = "/".join(self.uuri.fragment.split("/")[:-1])
            filename = self.uuri.fragment.split("/")[-1]
            files = self.conn_object.listPath(
                self.uuri.get_samba_share(),
                fragment_directory,
            )
            return any(f.filename == filename for f in files)
        except OperationFailure:
            return False

    def _remote_path_exists(self) -> bool:
        """Verify if the referenced remote path (directory) exists.

        Returns:
            True if remote path exists, False otherwise.
        """
        try:
            fragment_directory = "/".join(self.uuri.fragment.split("/")[:-1])
            self.conn_object.listPath(self.uuri.get_samba_share(), fragment_directory)
        except OperationFailure:
            return False
        else:
            return True

    def _get_files_recursively(self, subpath: str | Path) -> list:
        """Recursively get all files in a subdirectory of the SMB share.

        Args:
            subpath: Path to the folder on the share.

        Returns:
            List of file paths (as strings).
        """
        listed_objects = self.conn_object.listPath(self.uuri.get_samba_share(), subpath)
        smb_objects = []
        for obj in listed_objects:
            if obj.filename in (".", ".."):
                continue
            if obj.isDirectory is True:
                smb_objects.extend(
                    self._get_files_recursively(subpath=subpath + "/" + obj.filename),
                )
            else:
                smb_objects.append(subpath + "/" + obj.filename)
        return smb_objects

    def list_container_items(
        self,
        pattern: str | None = None,
        subpath: str = "/",
    ) -> list:
        """Get objects in folder/'container'.

        Can be filtered by a regex pattern.

        Args:
            pattern: Regex pattern for filtering filenames.
            subpath: Folder path on the SMB share to list objects in.

        Returns:
            List of object names matching the filter.
        """
        if pattern is not None:
            container_objects = [
                f for f in container_objects if re.search(pattern, f) is not None
            ]
        return container_objects

    def _create_fragment_directory(self) -> None:
        """Create local folder structure on remote SMB location as needed.

        Iterates over all levels and creates directories if they do not exist.
        """
        fragment_dirs = self.uuri.fragment.split("/")[:-1]

        for level, _directory in enumerate(fragment_dirs):
            path_to_create = "/".join(fragment_dirs[: level + 1])
            try:
                self.conn_object.createDirectory(
                    self.uuri.get_samba_share(),
                    path_to_create,
                )
            except OperationFailure as e:
                msg = f"Could not create folder {path_to_create} with {e}"