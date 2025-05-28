
import contextlib
import logging
import re

from typing import ParamSpec

from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ServiceRequestError,
)
from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import DataLakeServiceClient


P = ParamSpec("P")


class IOAzureDL(UIOBase):
    """UIO class interface for Azure DataLake file objects.

    Handles connections, uploads, downloads, metadata retrieval and listing for DataLake files.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Initialize UIO class for Azure DataLake file storage.

        Args:
            kwargs: Requires 'uuri' to set connection and file attributes.

        Example:
            az-dl://<account>.dfs.core.windows.net/<filesystem>/sub_dir_path#<object>
        """
        super().__init__(**kwargs)
        self.client_keys = ["tenant-id", "client-id"]
        for key_name in self.client_keys:
            if key_name not in self.uuri.query:
                msg = f"DataLake '{key_name}' was not found in the query!"
                raise OSError(msg)
        account_name = self.uuri.user
        self.datalake_service_client = DataLakeServiceClient(
            account_url=f"https://{account_name}.dfs.core.windows.net",
            credential=ClientSecretCredential(
                tenant_id=self.uuri.query.get("tenant-id"),
                client_id=self.uuri.query.get("client-id"),
                client_secret=self.uuri.password,
            ),
        )

        available_file_systems = [
            x["name"] for x in self.datalake_service_client.list_file_systems()
        ]
            msg = (
                f". Available file systems are: {sorted(available_file_systems)}"
            )
            raise OSError(msg)

        self.file_system_client = self.datalake_service_client.get_file_system_client(
        )
        self.directory_client = self.file_system_client.get_directory_client(
            directory="/".join(
        )
        self.object_directory_client = self.file_system_client.get_directory_client(
        )
        self.file_client = self.directory_client.get_file_client(
        )
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
        )

    def __del__(self) -> None:
        """Close datalake connection on object deletion."""

    @property
    def remote_path(self) -> str | None:
        """Remote path is not directly applicable to DataLake files.

        Returns:
            None.
        """
        return None

    def get_file_properties(self) -> dict | None:
        """Get properties associated with the referenced file.

        Returns:
            Dictionary of file properties, or None if file does not exist.
        """
        if self.remote_object_exists() is True:
            return self.file_client.get_file_properties()
        return None

    def get_remote_tags(self) -> dict | None:
        """Get remote tags (metadata) associated with the file.

        Returns:
            Dictionary of file metadata, or None if file does not exist.
        """
        if self.remote_object_exists() is True:
            return self.get_file_properties()["metadata"]
        return None

    def get_object(self) -> str | None:
        """Get DataLake file path for referenced UUri if file exists.

        Returns:
            File path on the share, or None if file does not exist.
        """
        if self.remote_object_exists() is True:
            return self.get_file_properties()["name"]
        return None

    def download(self) -> None:
        """Download referenced remote object and write to local scratch path.

        If the file is not found or there are connection errors, a RuntimeError is raised.
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
        """Upload local object from scratch path to remote DataLake location.

        Args:
            tags: Optional dictionary of metadata tags to attach to the file.
                  Client keys are removed from the tag dictionary before upload.

        Raises:
            RuntimeError if upload fails.
        """
        file_dir_list = self.file_client.path_name.split("/")[:-1]
        for n in range(len(file_dir_list)):
            tmp_dir_client = self.file_system_client.get_directory_client(
            )
            with contextlib.suppress(ResourceExistsError):
                tmp_dir_client.create_directory()
        try:
            self.file_client.create_file()
            for keyname in self.client_keys:
                if tags is not None:
                    tags.pop(keyname, None)

                self.file_client.upload_data(data, metadata=tags, overwrite=True)
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
            self.file_client.set_metadata(tags)

    def remote_object_exists(self) -> bool:
        """Check if the referenced remote object exists.

        Returns:
            True if the remote file exists, otherwise False.
        """
        return self.file_client.exists()

    def _remote_path_exists(self) -> bool:
        """Check if the referenced remote directory path exists.

        Returns:
            True if the remote directory exists, otherwise False.
        """
        try:
            self.directory_client.get_directory_properties()
        except ResourceNotFoundError:
            return False
        else:
            return True

        """List all objects in the file system (container), optionally filtering by regex pattern.

        Args:
            pattern: Optional regex pattern to filter object names.

        Returns:
            List of object names matching the filter, or all object names if no pattern is provided.
        """
        container_objects = self.file_system_client.get_paths(recursive=False)
        if pattern is not None:
            container_objects = [
                f for f in container_objects if re.search(pattern, f) is not None
            ]
        return container_objects