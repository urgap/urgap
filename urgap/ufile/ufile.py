import shutil
from pathlib import Path
from urllib.parse import urlparse, urlunparse


class UFile:

    def __init__(
        self,
        self._local_copy = None
        self._io = None

        self._io = None

    @property

    @property
        return self.io.scratch_path




    @property

    @property
        object_name = self.object_name

    @property


    @property
            )

    @property


    @property

        Returns:
        """
        if self._io is None:
        return self._io

    @classmethod

        Args:

        Returns:
        """


        Returns:
        """


        Returns:

        """


        )
        self._io = None
        try:

        self.io.create_container()

        self.io.remove_remote_object()

        self.purge_local_file()
        self.purge_local_tags()

            self.io.scratch_path.unlink()
