"""Urgap uri dict class."""

import ast
import getpass
import logging
import re

from pathlib import Path

import urgap

logger = logging.getLogger(__name__)


class UUri:
    """A normalized UUri parser and container for Urgap.

    This class encapsulates the components of a UUri or UCFS string as attributes,
    parses them, and provides helpers to access the elements as a dict.
    It also extracts tags from queries and can handle different storage backends.
    """

        self._user = None
        self._password = None
        self.scheme = self.uri_dict["scheme"]
        self.netloc = self.uri_dict["netloc"]
        self.path = self.uri_dict["path"]
        self.params = self.uri_dict["params"]
        self.original_query = self.uri_dict["query"]
        self.fragment = self.uri_dict["fragment"]

        if len(self.path) > 1 and self.path.endswith("/"):
            self.path = self.path.rstrip("/")
        self.query = self.parse_query_tags()
        self.check_fragment_integrity()

    def parse_query_tags(self) -> dict:
        """Parse a query string into a dictionary, inferring types for each value.

        Returns:
            Dictionary of parsed query tags.
        """

        def infer_type(
            value: str,
        ) -> str | int | float | bool | list | dict | tuple | None:
            """Infer the type of a string value using ast.literal_eval.

            Arguments:
                value: The string to convert.

            Returns:
                The inferred value in its appropriate Python type.
            """
            try:
                return ast.literal_eval(value)
            except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
                return value

        if "=" in self.original_query:
            param_vals = self.original_query.lstrip("?").split("&")
            query = {
                key: infer_type(val)
                for key, val in (pv.split("=", maxsplit=1) for pv in param_vals)
            }
        else:
            query = {}
        return query

    def check_fragment_integrity(self) -> None:
        """Validate that query parameters are not incorrectly placed in the fragment.

        Raises:
            ValueError: If query content is found in the fragment string.
        """
        if "=" in self.fragment and "?" in self.fragment:
            msg = "Query should be in url part of the UUri but was found in the fragment instead."
            raise ValueError(msg)

    @property
    def user(self) -> str | None:
        """Return the username for this UUri. If not already set, attempts to load it.

        Returns:
            str: Username associated with this UUri, or empty string if not found.
        """
        if self._user is None:
            self._get_credentials()
        return self._user

    @property
    def password(self) -> str | None:
        """Return the password for this UUri. If not already set, attempts to load it.

        Returns:
            str: Password associated with this UUri, or empty string if not found.
        """
        if self._password is None:
            self._get_credentials()
        return self._password

    def _get_credentials(self) -> None:
        """Attempt to load credentials for this UUri's scheme and netloc, unless it's a local or https UUri.

        If found, sets _user and _password attributes using Urgap's credential manager.
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
                credentials = urgap.instances.ucredential_manager.extract_credentials(
                    cred_key,
                )
                msg = f"Set credentials for {credentials['user']}"
                logger.debug(msg)
            except KeyError:
                msg = f"No credentials entry found in .urgap/credentials_lookup.json for {cred_key}"
                logger.warning(msg)
                credentials = {"user": getpass.getuser(), "password": None}
            self._user = credentials["user"]
            self._password = credentials["password"]

    @property
    def storage_uri(self) -> str:
        """Get the storage_uri."""
        if self.path == "":
            return f"{self.scheme}://{self.netloc}"
        return f"{self.scheme}://{self.netloc}{self.path}"

    @property
    def mylabdata_api_url(self) -> str | None:
        """Get the api_url."""
        if self.scheme == "mylabdata":
            return self.get_mylabdata_api_url()
        return None

    def get_mylabdata_api_url(self) -> str:
        """Get the api_url."""
        return f"https://{self.netloc}"

    @property
    def mylabdata_api_url_files(self) -> str | None:
        """Get the api_url_files."""
        if self.scheme == "mylabdata":
            return self.get_mylabdata_api_url_files()
        return None

    def get_mylabdata_api_url_files(self) -> str:
        """Get the api_url_files."""
        return self.get_mylabdata_api_url() + "/files"

    @property
    def samba_share(self) -> str | None:
        """Get the samba_share."""
        if self.scheme == "smb":
            return self.get_samba_share()
        return None

    def get_samba_share(self) -> str:
        """Get the samba_share."""
        return self.path.lstrip("/")

    @property
    def azure_share(self) -> str | None:
        """Get the share."""
        if self.scheme in ("az-dl", "az-smb"):
            return self.get_azure_share()
        return None

    def get_azure_share(self) -> str:
        """Get the share."""
        split_path = self.path.lstrip("/").split("/")
        return split_path[0]

    @property
    def azure_directory_list(self) -> list | None:
        """Get the directory_list."""
        if self.scheme in ("az-dl", "az-smb"):
            return self.get_azure_directory_list()
        return None

    def get_azure_directory_list(self) -> list:
        """Get the directory_list."""
        split_path = self.path.lstrip("/").split("/")
        return split_path[1:]

    @property
    def azure_object_file(self) -> str | None:
        """Get the object_file."""
        if self.scheme in ("az-dl", "az-smb"):
            return self.get_azure_object_file()
        return None

    def get_azure_object_file(self) -> str:
        """Get the object_file."""
        split_object = self.fragment.split("/")
        return split_object[-1]

    @property
    def azure_object_directory_list(self) -> list | None:
        """Get the object_directory_list."""
        if self.scheme in ("az-dl", "az-smb"):
            return self.get_azure_object_directory_list()
        return None

    def get_azure_object_directory_list(self) -> list:
        """Get the object_directory_list."""
        split_object = self.fragment.split("/")
        if len(split_object) > 1:
            return split_object[:-1]
        return []

    @property
    def file_remote_path(self) -> Path | None:
        """Get the file_remote_path."""
        if self.scheme == "file":
            return self.get_file_remote_path()
        return None

    def get_file_remote_path(self) -> Path:
        """Get the file_remote_path."""
        return (
            Path(self.path).parent / self.get_container_name() / self.get_object_name()
        ).resolve()

    @property
    def file_remote_tag_path(self) -> Path | None:
        """Get the file_remote_tag_path."""
        if self.scheme == "file":
            return self.get_file_remote_tag_path()
        return None

    def get_file_remote_tag_path(self) -> Path:
        """Get the file_remote_tag_path."""
        return (
            self.get_file_remote_path().parent
            / (self.get_file_remote_path().name + ".tag")
        ).resolve()

    @property
    def https_remote_path(self) -> str | None:
        """Get the https_remote_path."""
        if self.scheme == "https":
            return self.get_https_remote_path()
        return None

    def get_https_remote_path(self) -> str:
        """Get the https_remote_path."""
        return f"{self.scheme}://{self.netloc}{self.path}/{self.fragment}"

    @property
    def https_remote_tag_path(self) -> str | None:
        """Get the https_remote_tag_path."""
        if self.scheme == "https":
            return self.get_https_remote_tag_path()
        return None

    def get_https_remote_tag_path(self) -> str:
        """Get the https_remote_tag_path."""
        return self.get_https_remote_path() + ".tag"

    @property
    def host(self) -> str | None:
        """Get the host."""
            return self.get_host()
        return None

    def get_host(self) -> str | None:
        """Get the host."""
        if ":" in self.netloc:
            return self.netloc.split(":")[0]
        return None

    @property
    def port(self) -> str | None:
        """Get the port."""
            return self.get_port()
        return None

    def get_port(self) -> str | None:
        """Get the port."""
        if ":" in self.netloc:
            return self.netloc.split(":")[1]
        return None

    @property
    def container_name(self) -> str:
        """Get the container_name."""
        return self.get_container_name()

    def get_container_name(self) -> str:
        """Get the container_name."""
        return Path(self.path).name or self.netloc

    @property
    def object_name(self) -> str:
        """Get the object_name."""
        return self.get_object_name()

    def get_object_name(self) -> str:
        """Get the object_name."""
        return self.fragment

    @property
    def github_resource_name(self) -> str | None:
        """Get the github resource name."""
        if self.scheme == "github":
            return self.get_github_resource_name()
        return None

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
                return "/".join(segments[2:])
            case _:
                msg = "Unknown param for github resource"
                raise KeyError(msg)

    @property
    def mylabdata_url(self) -> str | None:
        if self.scheme == "mylabdata":
            return self.get_mylabdata_url()
        return None

    def get_mylabdata_url(self) -> str:
        encoded_fragment = quote(self.fragment, safe="")
        return f"{self.get_mylabdata_api_url_files()}{self.path}/{encoded_fragment}"