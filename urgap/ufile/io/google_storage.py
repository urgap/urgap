import logging
import re

from google.cloud import storage



class IOGoogleCloudStorage(UIOBase):

        """Create new UIO class for processing Google Cloud Storage.

        Args:
        """

    @property
        """Get remote file path.

        Returns:
        """
        return None

    @property
        """Get remote file tag path.

        Returns:
        """
        return None

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
            else:


        Args:

        Returns:
        """
        return container_objects


        Returns:
        """
        return self.blob.exists()