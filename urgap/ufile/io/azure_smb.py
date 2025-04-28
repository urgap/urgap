
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

    def __init__(self, **kwargs: P.kwargs) -> None:

        Args:

        """
        super().__init__(**kwargs)
        self.share_service_client = ShareServiceClient(
        )
        available_shares = [x["name"] for x in self.share_service_client.list_shares()]
            msg = (
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

        Returns:
        """
        return None

    def get_file_properties(self) -> dict | None:

        Returns:
        """
        return self.file_client.get_file_properties()

    def get_remote_tags(self) -> dict | None:

        Returns:
        """


        Returns:
        """

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
        ) as e:
            self.scratch_path.unlink(missing_ok=True)
            raise RuntimeError from e

    def upload(self, tags: dict | None = None) -> None:
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

    def list_container_items(
    ) -> list:

        Args:

        Returns:
        """
        if pattern is not None:
            container_objects = [
                f for f in container_objects if re.search(pattern, f) is not None
            ]
        return container_objects