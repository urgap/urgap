
import ast
import getpass
import logging
import re

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
        if self.scheme == "github":
            cred_key = (
                f"{self.scheme}://{self.netloc}/"
                f"{self.get_github_resource_name('org')}/{self.get_github_resource_name('repo')}"
            )
        else:
            cred_key = f"{self.scheme}://{self.netloc}"
        if self.scheme not in ("file", "https"):
            try:
                    cred_key,
                )
                msg = f"Set credentials for {credentials['user']}"
            except KeyError:
                credentials = {"user": getpass.getuser(), "password": None}
            self._user = credentials["user"]
            self._password = credentials["password"]

        """Get the api_url."""

        """Get the api_url_files."""

    def get_samba_share(self) -> str:
        """Get the samba_share."""
        return self.path.lstrip("/")

        """Get the share."""
        split_path = self.path.lstrip("/").split("/")
        return split_path[0]

        """Get the directory_list."""
        split_path = self.path.lstrip("/").split("/")
        return split_path[1:]

        """Get the object_file."""
        split_object = self.fragment.split("/")
        return split_object[-1]

        """Get the object_directory_list."""
        split_object = self.fragment.split("/")
        if len(split_object) > 1:
            return split_object[:-1]
        return []

    def get_file_remote_path(self) -> Path:
        """Get the file_remote_path."""
        return (
        ).resolve()

    def get_file_remote_tag_path(self) -> Path:
        """Get the file_remote_tag_path."""
        return (
            self.get_file_remote_path().parent
            / (self.get_file_remote_path().name + ".tag")
        ).resolve()

    def get_https_remote_path(self) -> str:
        """Get the https_remote_path."""


    def get_https_remote_tag_path(self) -> str:
        """Get the https_remote_tag_path."""
        return self.get_https_remote_path() + ".tag"

    def get_host(self) -> str | None:
        """Get the host."""
        if ":" in self.netloc:
            return self.netloc.split(":")[0]
        return None

    def get_port(self) -> str | None:
        """Get the port."""
        if ":" in self.netloc:
            return self.netloc.split(":")[1]
        return None


    def get_container_name(self) -> str:
        """Get the container_name."""
        return Path(self.path).name or self.netloc

    def get_object_name(self) -> str:
        """Get the object_name."""
        return self.fragment

    def get_github_resource_name(self, resource: str = "repo") -> str:
        """Get the github resource name."""
        path = self.path.lstrip("/").rstrip("/")
        segments = re.findall(r"[^/]+", path)
        match resource:
            case "org":
                return segments[0]
            case "repo":
                return segments[1]
            case "branch":
            case _:
                msg = "Unknown param for github resource"
                raise KeyError(msg)