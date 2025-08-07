"""Google Storage scheme subclass of urgap2's UIO submodule."""

import logging
import re

from typing import ParamSpec

from google.cloud import storage

import urgap

from urgap.ufile.io._base import UIOBase

P = ParamSpec("P")
logger = logging.getLogger(__name__)


class IOGoogleCloudStorage(UIOBase):
    """UIO class interface for Google Cloud Storage.

    Provides interaction and file operations for Google Cloud Storage buckets and objects.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new UIO class for processing Google Cloud Storage.

        Args:
            **kwargs: Passed to UIOBase. Must contain UUri and relevant parsed attributes.
        """
        super().__init__(**kwargs)
        self.bucket = self.client.bucket(bucket_name=self.uuri.get_container_name())
        self.blob = self.bucket.blob(self.uuri.get_object_name())

    @property
    def remote_path(self) -> str | None:
        """Get remote file path.

        Returns:
            Always None for Google Cloud Storage, as the full UUri is managed by GCS.
        """
        return None

    @property
    def remote_tag_path(self) -> str | None:
        """Get remote file tag path.

        Returns:
            Always None for Google Cloud Storage, as tags are stored as blob metadata.
        """
        return None

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with referenced file.

        Returns:
            Dictionary of metadata tags if the blob exists, otherwise None.
        """
        blob = self.bucket.get_blob(self.uuri.get_object_name())
        if blob is None:
            return None
        return blob.metadata

    def upload(self, tags: dict | None = None) -> None:
        """Upload scratch file to remote location with associated tags.

        Args:
            tags: Optional dictionary of metadata to set for the blob.
        """
        if tags is None:
            logger.warning("No tags provided, skipping upload.")
        else:
            self.blob.metadata = tags
        self.blob.upload_from_filename(filename=self.scratch_path)

    def download(self) -> None:
        """Download file to scratch path from remote location.

        Checks local hash and remote hash (if tags present); downloads only if different or not present.
        Logs a message if remote does not exist.
        """
        download_object = False
        if self.scratch_path.exists():
            local_hash = urgap.ucore.calculate_file_hash(
                input_file=self.scratch_path,
                hash_algorithm=urgap.config["hash_algorithm"],
            )
            remote_tags = self.get_remote_tags()
            if remote_tags is not None:
                remote_hash = remote_tags.get(
                    urgap.config["hash_algorithm"],
                    "Have you ever questioned the nature of your reality?",
                )
                if local_hash != remote_hash:
                    download_object = True
            else:
                download_object = False
        else:
            download_object = True
        if download_object is True:
            if self.remote_object_exists():
                self.blob.download_to_filename(filename=self.scratch_path)
                msg = f"Downloaded {self.blob.name} into {self.scratch_path.parent}"
                logger.debug(msg)
            else:
                msg = f"{self.blob.name} does not exist remotely. Skipping download."
                logger.warning(msg)

        """Get objects in folder/'container', optionally filtered by a regex pattern.

        Args:
            pattern: Optional regex pattern for filtering blob names.

        Returns:
            List of blob names (strings) matching the pattern, or all if pattern is None.
        """
        return container_objects

    def remote_object_exists(self) -> bool:
        """Check if object exists in the container.

        Returns:
            True if the blob exists, otherwise False.
        """
        return self.blob.exists()