"""file scheme subclass of urgap2's UIO submodule."""

import json
import logging
import os
import re
import shutil

from pathlib import Path
from typing import ParamSpec

from urgap.ufile.io._base import UIOBase

P = ParamSpec("P")
logger = logging.getLogger(__name__)


class IOPython(UIOBase):
    """UIO Class interface for regular Python file objects.

    Provides basic file IO for local files on disk.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new UIO class for processing file scheme.

        Args:
            **kwargs: Requires 'uuri' to set up the object and path information.
        """
        super().__init__(**kwargs)
        self.driver = "Local Python Power :)"

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with referenced file.

        Returns:
            Dictionary with tags/metadata if present, else None.
        """
        tags = None
        try:
            with self.uuri.get_file_remote_tag_path().open() as f:
                tags = json.load(f)
        except FileNotFoundError:
            pass
        return tags

    def get_object(self) -> Path:
        """Get the referenced UUri as a local Path.

        Returns:
            Path object of the file.
        """
        return self.uuri.get_file_remote_path()

    def download(self) -> None:
        """Download referenced remote object (copy from remote_path to scratch_path).

        If the file does not exist, a debug message is logged.
        """
        try:
            shutil.copyfile(self.uuri.get_file_remote_path(), self.scratch_path)
        except FileNotFoundError:
            msg = f"File {self.uuri.get_file_remote_path()} does not exist"
            logger.debug(msg)

    def upload(self, tags: dict | None = None) -> None:
        """Upload local scratch file and associated tag to remote location.

        Args:
            tags: Optional dictionary with metadata to store as .tag file.

        Raises:
            OSError: If the file cannot be copied.
        """
        self.uuri.get_file_remote_path().parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copyfile(self.scratch_path, self.uuri.get_file_remote_path())
            if tags is not None:
                with (
                    self.uuri.get_file_remote_tag_path().open("w") as remote_tag_file,
                ):
                    json.dump(tags, remote_tag_file)
        except OSError as e:
            msg = f"Could not copy file {self.scratch_path} due to {e}"
            logger.warning(msg)
            raise OSError(msg) from e

    def remote_object_exists(self) -> bool:
        """Verify referenced remote object exists.

        Returns:
            True if the file exists on disk, otherwise False.
        """
        return self.uuri.get_file_remote_path().exists()

    def create_container(
        self,
        exist_ok: bool = True,
    ) -> None:
        """Create a new container (folder) at referenced remote location.

        Args:
            exist_ok: Whether it is okay if the directory already exists.
        """
        container_folder = self.uuri.get_file_remote_path().parent
        msg = f"Creating {container_folder} if needed"
        logger.debug(msg)
        container_folder.mkdir(exist_ok=exist_ok, parents=True)

    def get_container(self, container_name: str | None = None) -> os.PathLike:
        """Get container (directory) Path.

        Args:
            container_name: Name of the container/folder. If None, uses self.uri.container_name.

        Returns:
            Path object pointing to the container directory.
        """
        if container_name is None:
            container_name = self.uuri.get_container_name()
        return Path(self.uuri.path).parent / container_name

    def list_container_items(
        self,
        container_name: str | None = None,
        pattern: str | None = None,
        full_string: bool = False,
    ) -> list:
        """Get all objects in a container (directory), optionally filtered by pattern.

        Args:
            container_name: Name of the container or bucket. If None, uses self.container_name.
            pattern: Optional regex pattern for filtering file names.
            full_string: Whether to return the list with full strings or just fragments.

        Returns:
            List of object names (relative paths) in the container matching the pattern.
        """
        container = self.get_container(container_name=container_name)
        container_objects = []
        for obj in container.glob("**/*"):
            try:
                is_file = obj.is_file()
            except PermissionError:
                msg = f"Cannot determine if {obj} is file or directory, skipping..."
                logger.debug(msg)
                continue
            if is_file:
                name = str(obj).replace(str(container), "").lstrip("/")
                container_objects.append(name)
        if full_string is True:
            container_objects = self.add_storage_uri_to_container_items(
                container_objects,
            )
        else:
            logger.warning(
                "DeprecationWarning: list_container_items with full_string=False will be deprecated soon, use full_string=True instead.",
            )
        if pattern is not None:
            container_objects = [
                f for f in container_objects if re.search(pattern, f) is not None
            ]
        return container_objects

    def remove_remote_object(self) -> None:
        """Delete referenced remote location file and associated .tag file, if present."""
        self.uuri.get_file_remote_path().unlink(missing_ok=True)
        self.uuri.get_file_remote_tag_path().unlink(missing_ok=True)
