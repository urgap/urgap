"""Azure Blob scheme subclass of urgap2's UIO submodule."""

import json
import logging
import re
import sys

from typing import ParamSpec

from azure.storage.blob import BlobServiceClient

import urgap

from urgap.ufile.io._base import UIOBase

P = ParamSpec("P")
logger = logging.getLogger(__name__)


class IOAzureBlobStorage(UIOBase):
    """UIO class interface for Azure Blob Storage.

    Provides methods for uploading, downloading, and listing blobs, as well as fetching blob metadata.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Initialize the Azure Blob Storage IO class.

        Args:
            kwargs: Passed to UIOBase. Requires "uri" for connection setup.
        """
        super().__init__(**kwargs)
        self.container = self.client.get_container_client(
            container=self.uuri.get_container_name(),
        )
        self.blob = self.container.get_blob_client(self.uuri.get_object_name())

    @property
    def remote_path(self) -> None:
        """Azure blobs do not have a traditional remote path.

        Returns:
            None.
        """
        return None

    @property
    def remote_tag_path(self) -> None:
        """Azure blobs do not have a separate remote tag path.

        Returns:
            None.
        """
        return None

    def get_file_properties(self) -> dict | None:
        """Get properties associated with the referenced file.

        Returns:
            Dictionary with properties of the file, or None if not found.
        """
        return self.blob.get_blob_properties()

    def get_remote_tags(self) -> dict | None:
        """Get remote tags (metadata) for the referenced blob.

        Returns:
            The dictionary of metadata tags, creation_time, last_modified if the object exists, otherwise None.
        """
        if self.remote_object_exists():
            props = self.get_file_properties()
            r_tags = {}
            if props.get("metadata") is not None:
                r_tags.update(props.get("metadata"))
            for k in ["creation_time", "last_modified"]:
                if props.get(k) is not None:
                    r_tags[k] = props.get(k).isoformat()
            return r_tags
        return None

    def upload(self, tags: dict | None = None) -> None:
        """Upload the scratch file to the remote blob, attaching provided tags as metadata.

        Args:
            tags: Dictionary of metadata tags to write to remote location. If too many, parent keys are removed.
        """
        if tags is None:
            tags = {}
            logger.warning("No tags provided, skipping upload.")
        if (len(tags.keys()) > 100) or (sys.getsizeof(json.dumps(tags)) > 7000):
            msg = (
                f"Too many keys for azure blob storage in {self.uuri.fragment}. "
                f"Removing parent keys and dot_str from tags."
            )
            logger.warning(msg)
            tags = {
                k: v
                for k, v in tags.items()
                if not k.startswith(("parent_", "dot_str_"))
            }
            tags["ParentsRemoved"] = "Yes"
            tags["DotStrRemoved"] = "Yes"

        with self.scratch_path.open("rb") as data:
            self.blob.upload_blob(data, metadata=tags, overwrite=True)

    def download(self) -> None:
        """Download the blob to the scratch path from remote storage.

        Downloads only if the local file is missing or the hash does not match the remote.
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
                with self.scratch_path.open("wb") as local_blob:
                    blob_data = self.blob.download_blob()
                    blob_data.readinto(local_blob)
                msg = (
                    f"Downloaded {self.blob.blob_name} into {self.scratch_path.parent}"
                )
                logger.debug(msg)
            else:
                msg = (
                    f"{self.blob.blob_name} does not exist remotely. Skipping download."
                )
                logger.warning(msg)

    def list_container_items(
        self,
        pattern: str | None = None,
        full_string: bool = False,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list:
        """List all objects in the Azure container, optionally filtering by regex pattern.

        Args:
            pattern: Regular expression pattern to filter blob names.
            full_string: Whether to return the list with full strings or just fragments.
            start_date: ISO format datetime string to filter blobs modified after this date.
            end_date: ISO format datetime string to filter blobs modified before this date.

        Returns:
            A list of blob names that match the pattern, or all blob names if pattern is None.
        """
            blobs = self.container.list_blobs()
            container_objects = []
            for blob in blobs:
        if full_string is True:
            container_objects = self.add_storage_uri_to_container_items(
                container_objects,
            )
        else:
            logger.warning(
                "DeprecationWarning: list_container_items with full_string=False will be deprecated soon, use full_string=True instead.",
            )

        return container_objects

    def remote_object_exists(self) -> bool:
        """Check if the blob exists in the container.

        Returns:
            True if the blob exists, otherwise False.
        """
        return self.blob.exists()