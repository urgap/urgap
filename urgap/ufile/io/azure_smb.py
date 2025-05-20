
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



P = ParamSpec("P")


class IOAzureSMB(UIOBase):
    """UIO class interface for SMB file objects in Azure File Storage.

    Handles connecting, reading, writing, and listing objects on Azure file shares using SMB.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new UIO class for processing Azure file storage SMB scheme.

        Args:

        Notes:
            Uses SAS token to access. Expiration can be set by &sas_expiration_in_h in the UUri query.
            Example UUri:
                az-smb://<account>.file.core.windows.net/<share>/sub_dir_path#<object>
        """
        super().__init__(**kwargs)
        self.share_service_client = ShareServiceClient(
        )
        available_shares = [x["name"] for x in self.share_service_client.list_shares()]
            msg = (
                f" Available shares are: {sorted(available_shares)}"
            )
            raise OSError(msg)
        self.directory_client = self.share_client.get_directory_client(
        )
        self.object_directory_client = self.share_client.get_directory_client(
        )
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
        )

    def __del__(self) -> None:

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

        Returns:
        """

        """Get the SMB file path for the referenced UUri.

        Returns:
            Path of the file on the share.
        """

    def download(self) -> None:
        """Download referenced remote object and write to local scratch path.

        If the file cannot be found or there are connection errors, a RuntimeError is raised.
        """
        try:
            download = self.file_client.download_file()
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
            )
            with contextlib.suppress(ResourceExistsError):
                tmp_dir_client.create_directory()
        try:
                self.file_client.upload_file(data)
        except (
            AzureError,
            ServiceRequestError,
            ClientAuthenticationError,
            ResourceNotFoundError,
            HttpResponseError,
        ) as e:
            msg = f"File {self.scratch_path} couldn't be uploaded!"
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
    ) -> list:
        """Get all objects in a folder/'container', recursively, with optional regex filtering.

        Args:
            pattern: Optional regex pattern for filtering returned file names.
            limit: Optional limit for the number of objects returned.

        Returns:
            List of object names matching the filter (or all if no filter/limit).
        """
        if pattern is not None:
            container_objects = [
                f for f in container_objects if re.search(pattern, f) is not None
            ]
        return container_objects