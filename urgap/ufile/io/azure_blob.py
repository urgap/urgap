import logging
import re

from azure.storage.blob import BlobServiceClient



class IOAzureBlobStorage(UIOBase):


        Args:
        """

    @property

        Returns:
        """
        return None

    @property

        Returns:
        """
        return None


        Returns:
        """
        if self.remote_object_exists():


        Args:
        """
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
                    f"Downloaded {self.blob.blob_name} into {self.scratch_path.parent}"
                )
            else:
                    f"{self.blob.blob_name} does not exist remotely. Skipping download."
                )

        Args:

        Returns:
        """
        return container_objects


        Returns:
        """
        return self.blob.exists()