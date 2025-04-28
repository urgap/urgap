
import json
import logging
import os
import re
import shutil

from pathlib import Path
from typing import ParamSpec


P = ParamSpec("P")


class IOPython(UIOBase):

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new UIO class for processing file scheme.

        Args:
        """
        super().__init__(**kwargs)
        self.driver = "Local Python Power :)"

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with referenced file.

        Returns:
        """
        tags = None
        try:
                tags = json.load(f)
        except FileNotFoundError:
            pass
        return tags

    def get_object(self) -> Path:

        Returns:
        """

    def download(self) -> None:

        """
        try:
        except FileNotFoundError:

    def upload(self, tags: dict | None = None) -> None:
        try:
            if tags is not None:
                    json.dump(tags, remote_tag_file)
        except OSError as e:
            msg = f"Could not copy file {self.scratch_path} due to {e}"
            raise OSError(msg) from e

    def remote_object_exists(self) -> bool:
        """Verify referenced remote object exists.

        Returns:
        """

    def create_container(
        self,
        exist_ok: bool = True,
    ) -> None:

        Args:
        """
        msg = f"Creating {container_folder} if needed"
        container_folder.mkdir(exist_ok=exist_ok, parents=True)

    def get_container(self, container_name: str | None = None) -> os.PathLike:

        Args:

        Returns:
        """
        if container_name is None:

    def list_container_items(
        self,
        container_name: str | None = None,
        pattern: str | None = None,
    ) -> list:

        Args:

        Returns:
        """
        container = self.get_container(container_name=container_name)
        container_objects = []
        for obj in container.glob("**/*"):
            try:
                is_file = obj.is_file()
            except PermissionError:
                msg = f"Cannot determine if {obj} is file or directory, skipping..."
                continue
            if is_file:
                name = str(obj).replace(str(container), "").lstrip("/")

    def remove_remote_object(self) -> None: