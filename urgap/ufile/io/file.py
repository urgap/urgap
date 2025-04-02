
import json
import logging
import os
import re
import shutil
from pathlib import Path



class IOPython(UIOBase):

        """Create new UIO class for processing file scheme.

        Args:
        """
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


        Returns:
        """


        """
        try:
        except FileNotFoundError:

        try:
            if tags is not None:
                    json.dump(tags, remote_tag_file)

    def remote_object_exists(self) -> bool:
        """Verify referenced remote object exists.

        Returns:
        """

    def create_container(
        self,
        exist_ok: bool = True,

        Args:
        """
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
                continue
            if is_file:
                name = str(obj).replace(str(container), "").lstrip("/")
