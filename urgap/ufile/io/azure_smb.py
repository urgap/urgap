
import logging
import re




class IOAzureSMB(UIOBase):


        Args:

        """
        self.share_service_client = ShareServiceClient(
        )
        available_shares = [x["name"] for x in self.share_service_client.list_shares()]
            )
        self.directory_client = self.share_client.get_directory_client(
        )
        self.object_directory_client = self.share_client.get_directory_client(
        )
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
        )


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

        file_dir_list = self.file_client.directory_path.split("/")
        for n in range(len(file_dir_list)):
            tmp_dir_client = self.share_client.get_directory_client(
            )
                tmp_dir_client.create_directory()
        try:
                self.file_client.upload_file(data)
        except (
            AzureError,
            ServiceRequestError,
            ClientAuthenticationError,
            ResourceNotFoundError,
            HttpResponseError,

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