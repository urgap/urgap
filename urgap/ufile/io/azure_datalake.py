
import contextlib
import logging
import re

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



class IOAzureDL(UIOBase):


        Args:

        """
        self.client_keys = ["tenant-id", "client-id"]
        for key_name in self.client_keys:
                msg = f"DataLake '{key_name}' was not found in the query!"
                raise OSError(msg)
        self.datalake_service_client = DataLakeServiceClient(
            account_url=f"https://{account_name}.dfs.core.windows.net",
            credential=ClientSecretCredential(
            ),
        )

        available_file_systems = [
            x["name"] for x in self.datalake_service_client.list_file_systems()
        ]
            msg = (
            )
            raise OSError(msg)

        self.file_system_client = self.datalake_service_client.get_file_system_client(
        )
        self.directory_client = self.file_system_client.get_directory_client(
        )
        self.object_directory_client = self.file_system_client.get_directory_client(
        )
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
        )

    def __del__(self) -> None:
        """Close datalake connection on object deletion."""

    @property
    def remote_path(self) -> str | None:

        Returns:
        """
        return None

    def get_file_properties(self) -> dict | None:

        Returns:
        """
        if self.remote_object_exists() is True:
            return self.file_client.get_file_properties()
        return None

    def get_remote_tags(self) -> dict | None:

        Returns:
        """
        if self.remote_object_exists() is True:
            return self.get_file_properties()["metadata"]
        return None


        Returns:
        """
        if self.remote_object_exists() is True:
            return self.get_file_properties()["name"]
        return None

    def download(self) -> None:

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
            self.scratch_path.unlink(missing_ok=True)

    def upload(self, tags: dict | None = None) -> None:
        file_dir_list = self.file_client.path_name.split("/")[:-1]
        for n in range(len(file_dir_list)):
            tmp_dir_client = self.file_system_client.get_directory_client(
            )
            with contextlib.suppress(ResourceExistsError):
                tmp_dir_client.create_directory()
        try:
            self.file_client.create_file()
            for keyname in self.client_keys:

                self.file_client.upload_data(data, metadata=tags, overwrite=True)
        except (
            AzureError,
            ServiceRequestError,
            ClientAuthenticationError,
            ResourceNotFoundError,
            HttpResponseError,
            msg = f"File {self.scratch_path} couldn't be uploaded!"

        if tags is not None:
            self.file_client.set_metadata(tags)

    def remote_object_exists(self) -> bool:

        Returns:
        """
        return self.file_client.exists()

    def _remote_path_exists(self) -> bool:

        Returns:
        """
        try:
            self.directory_client.get_directory_properties()
        except ResourceNotFoundError:
            return False
        else:
            return True


        Args:

        Returns:
        """
        container_objects = self.file_system_client.get_paths(recursive=False)
        if pattern is not None:
            container_objects = [
                f for f in container_objects if re.search(pattern, f) is not None
            ]
        return container_objects