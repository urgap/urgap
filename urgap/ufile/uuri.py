
import ast
import getpass
import logging

from pathlib import Path



class UUri:

    This class encapsulates the components of a UUri or UCFS string as attributes,
    parses them, and provides helpers to access the elements as a dict.
    It also extracts tags from queries and can handle different storage backends.
    """

        self._user = None
        self._password = None

        if len(self.path) > 1 and self.path.endswith("/"):
            self.path = self.path.rstrip("/")
        self.check_fragment_integrity()

    @property
        """Return the username for this UUri. If not already set, attempts to load it.

        Returns:
        """
        if self._user is None:
            self._get_credentials()
        return self._user

    @property
        """Return the password for this UUri. If not already set, attempts to load it.

        Returns:
        """
        if self._password is None:
            self._get_credentials()
        return self._password

    def _get_credentials(self) -> None:
        """Attempt to load credentials for this UUri's scheme and netloc, unless it's a local or https UUri.

        """
        if self.scheme not in ("file", "https"):
            try:
                )
                msg = f"Set credentials for {credentials['user']}"
            except KeyError:
                credentials = {"user": getpass.getuser(), "password": None}
            self._user = credentials["user"]
            self._password = credentials["password"]



    def get_samba_share(self) -> str:
        return self.path.lstrip("/")

        split_path = self.path.lstrip("/").split("/")
        return split_path[0]

        split_path = self.path.lstrip("/").split("/")
        return split_path[1:]

        split_object = self.fragment.split("/")
        return split_object[-1]

        split_object = self.fragment.split("/")
        if len(split_object) > 1:
            return split_object[:-1]
        return []

    def get_file_remote_path(self) -> Path:
        return (
        ).resolve()

    def get_file_remote_tag_path(self) -> Path:
        return (
            self.get_file_remote_path().parent
            / (self.get_file_remote_path().name + ".tag")
        ).resolve()

    def get_https_remote_path(self) -> str:


    def get_https_remote_tag_path(self) -> str:
        return self.get_https_remote_path() + ".tag"

    def get_host(self) -> str | None:
        if ":" in self.netloc:
            return self.netloc.split(":")[0]
        return None

    def get_port(self) -> str | None:
        if ":" in self.netloc:
            return self.netloc.split(":")[1]
        return None


    def get_container_name(self) -> str:
        return Path(self.path).name or self.netloc

    def get_object_name(self) -> str:
        return self.fragment
