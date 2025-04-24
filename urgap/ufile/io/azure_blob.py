
import json
import logging
import re
import sys

from azure.storage.blob import BlobServiceClient




class IOAzureBlobStorage(UIOBase):


        Args:
        """

    @property
    def remote_path(self) -> None:

        Returns:
            None.
        """
        return None

    @property
    def remote_tag_path(self) -> None:

        Returns:
            None.
        """
        return None

    def get_remote_tags(self) -> dict | None:

        Returns:
        """
        if self.remote_object_exists():
        return None


        Args:
        """
        if (len(tags.keys()) > 100) or (sys.getsizeof(json.dumps(tags)) > 7000):
            msg = (
            )
            tags["ParentsRemoved"] = "Yes"

            self.blob.upload_blob(data, metadata=tags, overwrite=True)

    def download(self) -> None:
        download_object = False
        if self.scratch_path.exists():
            )
            remote_tags = self.get_remote_tags()
            if remote_tags is not None:
                )
                    download_object = True
            else:
                download_object = False
        else:
            download_object = True
        if download_object is True:
            if self.remote_object_exists():
                    blob_data = self.blob.download_blob()
                    blob_data.readinto(local_blob)
                msg = (
                    f"Downloaded {self.blob.blob_name} into {self.scratch_path.parent}"
                )
            else:
                msg = (
                    f"{self.blob.blob_name} does not exist remotely. Skipping download."
                )


        Args:

        Returns:
        """
        return container_objects

    def remote_object_exists(self) -> bool:

        Returns:
        """
        return self.blob.exists()