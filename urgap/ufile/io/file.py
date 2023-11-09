import json
import logging
import re
import shutil
from pathlib import Path



class IOPython(UIOBase):

        """Create new UIO class for processing file scheme.

        Args:
        """
        self.driver = "Local Python Power :)"

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

        """Verify referenced remote object exists.

        Returns:
        """


        Args:
        """
        container_folder.mkdir(exist_ok=exist_ok, parents=True)


        Args:

        Returns:
        """
        if container_name is None:


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
