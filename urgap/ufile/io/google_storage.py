
import logging
import re

from google.cloud import storage




class IOGoogleCloudStorage(UIOBase):

        """Create new UIO class for processing Google Cloud Storage.

        Args:
        """

    @property
    def remote_path(self) -> str | None:
        """Get remote file path.

        Returns:
        """
        return None

    @property
    def remote_tag_path(self) -> str | None:
        """Get remote file tag path.

        Returns:
        """
        return None

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with referenced file.

        Returns:
        """
        if blob is None:
            return None
        return blob.metadata

        """Upload scratch file to remote location with associated tags.

        Args:
        """
            self.blob.metadata = tags
        self.blob.upload_from_filename(filename=self.scratch_path)

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
                self.blob.download_to_filename(filename=self.scratch_path)
                msg = f"Downloaded {self.blob.name} into {self.scratch_path.parent}"
            else:
                msg = f"{self.blob.name} does not exist remotely. Skipping download."


        Args:

        Returns:
        """
        return container_objects

    def remote_object_exists(self) -> bool:

        Returns:
        """
        return self.blob.exists()