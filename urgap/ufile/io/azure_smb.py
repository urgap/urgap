"""Azure file SMB Share subclass of urgap's UIO submodule."""

import contextlib
import logging
import pprint
import re

from pathlib import Path
from typing import ParamSpec

from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ServiceRequestError,
)
from azure.storage.fileshare import DirectoryProperties, ShareServiceClient

import urgap

from urgap.ufile.io._base import UIOBase

P = ParamSpec("P")
logger = logging.getLogger(__name__)


class IOAzureSMB(UIOBase):
    """UIO class interface for SMB file objects in Azure File Storage.

    Handles connecting, reading, writing, and listing objects on Azure file shares using SMB.
    """

    SCHEMA = "az-smb"

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new UIO class for processing Azure file storage SMB scheme.

        Args:
            kwargs: Requires 'uuri' to set up the object and establish connection.

        Notes:
            Uses SAS token to access. Expiration can be set by &sas_expiration_in_h in the UUri query.
            Example UUri:
                az-smb://<account>.file.core.windows.net/<share>/sub_dir_path#<object>
        """
        super().__init__(**kwargs)
        self.share_service_client = ShareServiceClient(
            account_url=self.uuri.netloc,
            credential=self.uuri.password,
        )
        available_shares = [x["name"] for x in self.share_service_client.list_shares()]
        if self.uuri.get_azure_share() not in available_shares:
            msg = (
                f"Share {self.uuri.get_azure_share()} is not available on host {self.uuri.netloc}."
                f" Available shares are: {sorted(available_shares)}"
            )
            raise OSError(msg)
        self.share_client = self.share_service_client.get_share_client(
            self.uuri.get_azure_share(),
        )
        self.directory_client = self.share_client.get_directory_client(
            directory_path="/".join(
                self.uuri.get_azure_directory_list()
                + self.uuri.get_azure_object_directory_list(),
            ),
        )
        self.object_directory_client = self.share_client.get_directory_client(
            directory_path="/".join(self.uuri.get_azure_directory_list()),
        )
        self.file_client = self.directory_client.get_file_client(
            self.uuri.get_azure_object_file(),
        )
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
            logging.ERROR,
        )

    def __del__(self) -> None:
        """Close SMB connection and associated clients when object is deleted."""
        for attr in (
            "file_client",
            "directory_client",
            "share_client",
            "share_service_client",
        ):
            if hasattr(self, attr):
                delattr(self, attr)

    @property
    def remote_path(self) -> str | None:
        """Return the remote path of the file if available.

        Returns:
            None (Azure SMB does not provide a direct remote path).
        """
        return None

    def get_file_properties(self) -> dict | None:
        """Get properties associated with the referenced file.

        Returns:
            Dictionary with properties of the file, or None if not found.
        """
        return self.file_client.get_file_properties()

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with the referenced file.

        Returns:
            Dictionary of metadata, creation_time, last_modified, or None if not found.
        """
        if self.remote_object_exists():
            props = self.get_file_properties()
            r_tags = {}
            if props.get("metadata") is not None:
                r_tags.update(props.get("metadata"))
            for k in ["creation_time", "last_modified"]:
                if props.get(k) is not None:
                    r_tags[k] = props.get(k).isoformat()
            return r_tags
        return None

    def get_object(self) -> str | None:
        """Get the SMB file path for the referenced UUri.

        Returns:
            Path of the file on the share.
        """
        if self.remote_object_exists():
            return self.get_file_properties()["path"]
        return None

    def download(self) -> None:
        """Download referenced remote object and write to local scratch path.

        If the file cannot be found or there are connection errors, a RuntimeError is raised.
        """
        try:
            download = self.file_client.download_file()
            with self.scratch_path.open("wb") as ooo:
                download.readinto(ooo)
        except (
            AzureError,
            ServiceRequestError,
            ClientAuthenticationError,
            ResourceNotFoundError,
            HttpResponseError,
        ) as e:
            self.scratch_path.unlink(missing_ok=True)
            raise RuntimeError from e

    def upload(self, tags: dict | None = None) -> None:
        """Upload local object from scratch to the remote Azure SMB file share.

        Args:
            tags: Optional dictionary of metadata tags to attach to the file.

        Raises:
            RuntimeError if upload fails.
        """
        file_dir_list = self.file_client.directory_path.split("/")
        for n in range(len(file_dir_list)):
            tmp_dir_client = self.share_client.get_directory_client(
                directory_path="/".join(file_dir_list[: n + 1]),
            )
            with contextlib.suppress(ResourceExistsError):
                tmp_dir_client.create_directory()
        try:
            with self.scratch_path.open("rb") as data:
                self.file_client.upload_file(data)
                logger.info(pprint.pformat("File uploaded successfully!"))
        except (
            AzureError,
            ServiceRequestError,
            ClientAuthenticationError,
            ResourceNotFoundError,
            HttpResponseError,
        ) as e:
            msg = f"File {self.scratch_path} couldn't be uploaded!"
            logger.exception(msg)
            raise RuntimeError(msg) from e

        if tags is not None:
            self.file_client.set_file_metadata(tags)

    def remote_object_exists(self) -> bool:
        """Verify the referenced remote object exists.

        Returns:
            True if the remote file exists, otherwise False.
        """
        return self.file_client.exists()

    def _remote_path_exists(self) -> bool:
        """Verify the referenced remote directory path exists.

        Returns:
            True if the directory exists, otherwise False.
        """
        try:
            self.directory_client.get_directory_properties()
        except ResourceNotFoundError:
            return False
        else:
            return True

    def list_container_items(
        self,
        pattern: str | None = None,
        limit: int | None = None,
        full_string: bool = False,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list:
        """Get all objects in a folder/'container', recursively, with optional regex filtering.

        Args:
            pattern: Optional regex pattern for filtering returned file names.
            limit: Optional limit for the number of objects returned.
            full_string: Whether to return the list with full strings or just fragments.
            start_date: ISO format datetime string to filter blobs modified after this date.
            end_date: ISO format datetime string to filter blobs modified before this date.

        Returns:
            List of object names matching the filter (or all if no filter/limit).
        """
        if full_string is True:
            container_objects = self.add_storage_uri_to_container_items(
                self.list_all_files_with_paths(
                    self.object_directory_client,
                    limit=limit,
                    start_date=start_date,
                    end_date=end_date,
                ),
            )
        else:
            logger.warning(
                "DeprecationWarning: list_container_items with full_string=False will be deprecated soon, use full_string=True instead.",
            )
            container_objects = self.list_all_files_with_paths(
                self.object_directory_client,
                limit=limit,
                start_date=start_date,
                end_date=end_date,
            )
        if pattern is not None:
            container_objects = [
                f for f in container_objects if re.search(pattern, f) is not None
            ]
        return container_objects

    def list_all_files_with_paths(
        self,
        directory_client: urgap.UFile.io,
        current_path: str | Path | None = None,
        limit: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list:
        """Recursively list all files in the given directory client, including their paths.

        Args:
            directory_client: The Azure directory client to list files from.
            current_path: The current path prefix for recursion (default: None).
            limit: Optional limit for the number of files returned.
            start_date: ISO format datetime string to filter files modified after this date.
            end_date: ISO format datetime string to filter files modified before this date.

        Returns:
            List of file paths as strings.
        """
        files_with_paths = []

        for item in directory_client.list_directories_and_files():
            if current_path is None:
                item_path = item.name
            else:
                item_path = f"{current_path}/{item.name}"
            if item.is_directory:
                subdir_client = directory_client.get_subdirectory_client(item.name)
                subdir_files = self.list_all_files_with_paths(
                    subdir_client,
                    current_path=item_path,
                    limit=limit,
                    start_date=start_date,
                    end_date=end_date,
                )
                files_with_paths.extend(subdir_files)
            elif (not any([start_date, end_date])) or (
                self.is_within_date_range(
                    directory_client=directory_client,
                    item=item,
                    start_date=start_date,
                    end_date=end_date,
                )
            ):
                files_with_paths.append(f"{item_path}")
            if limit is not None and len(files_with_paths) >= limit:
                break
        return files_with_paths

    def is_within_date_range(
        self,
        directory_client: urgap.UFile.io,
        item: DirectoryProperties,
        start_date: str,
        end_date: str,
    ) -> bool:
        """Check if the item's last modified date is within the specified date range.

        Args:
            directory_client: The Azure directory client.
            item: The directory item to check.
            start_date: ISO format datetime string for the start date filter.
            end_date: ISO format datetime string for the end date filter.

        Returns:
            True if the item's last modified date is within the range, False otherwise.
        """
        file_client = directory_client.get_file_client(item.name)
        props = file_client.get_file_properties()
        last_modified_iso = props.last_modified.isoformat()
        return (last_modified_iso <= end_date) and (last_modified_iso >= start_date)
