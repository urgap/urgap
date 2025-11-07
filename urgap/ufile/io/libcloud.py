"""Libcloud scheme subclass of urgap2's UIO submodule."""

import contextlib
import json
import logging
import os
import re
import tempfile

from typing import ParamSpec

import libcloud
import requests

from libcloud.storage.base import Object
from libcloud.storage.providers import get_driver
from libcloud.storage.types import Provider

import urgap

from urgap.ufile.io._base import UIOBase

P = ParamSpec("P")
logger = logging.getLogger(__name__)


class IOLibcloud(UIOBase):
    """UIO Class interface for libcloud-backed file storage.

    Handles file and tag operations for local-libcloud, minio-libcloud, gcs, and azure schemes via libcloud.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Initialize a new IOLibcloud instance for working with remote object stores.

        Args:
            **kwargs: Passed to UIOBase. Must contain required keys for UUri and driver initialization.
        """
        super().__init__(**kwargs)
        self._driver = None
        self._is_remote = True
        self._object = None
        self._container = None

    @property
    def remote_path(self) -> str | None:
        """Get the remote file path for local-libcloud scheme.

        Returns:
            Path to the file on disk for 'local-libcloud' scheme, or None for other schemes.
        """
        if self.uuri.scheme == "local-libcloud":
            return (
                self.uuri.get_libcloud_project_folder()
                / self.uuri.get_container_name()
                / self.uuri.get_object_name()
            )
        return None

    @property
    def remote_tag_path(self) -> str | None:
        """Get the remote file tag path for local-libcloud scheme.

        Returns:
            Path to the .tag file for 'local-libcloud' scheme, or None for other schemes.
        """
        if self.uuri.scheme == "local-libcloud":
            return (
                self.uuri.get_libcloud_project_folder()
                / self.uuri.get_container_name()
                / (self.uuri.get_object_name() + ".tag")
            )
        return None

    @property
    def driver(self) -> libcloud.DriverType:
        """Return internal driver object, initializing if necessary.

        Returns:
            The libcloud driver object.
        """
        if self.uuri.scheme != "local-libcloud" and urgap.config["umeta"] == "json":
            logger.warning(
                "Using Libcloud (and not schema local-libcloud) requires a centralized umeta interface, "
                "such as mongodb or tinydb. You can set it in your ~/.urgap/urgap.config",
            )
        elif self._driver is None:
            self._driver = self.get_driver()
        return self._driver

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with the referenced file.

        Returns:
            Tags as a dictionary, or None if not found.
        """
        tags = None
        if self.uuri.scheme == "local-libcloud":
            with (
                contextlib.suppress(FileNotFoundError),
                self.remote_tag_path.open() as tags_file,
            ):
                tags = json.load(tags_file)
        elif self.driver is not None:
            with contextlib.suppress(
                libcloud.storage.types.ObjectDoesNotExistError,
                AttributeError,
            ):
                tags = self.object.meta_data
        return tags

    def get_driver(self) -> libcloud.DriverType | None:
        """Get the libcloud driver appropriate for the current scheme.

        Returns:
            The instantiated libcloud driver, or None if connection fails.

        Raises:
            OSError: If the scheme is unknown.
        """
        if self.uuri.scheme == "local-libcloud":
            driver_cls = get_driver(Provider.LOCAL)
            self.uuri.get_libcloud_project_folder().mkdir(parents=True, exist_ok=True)
            driver = driver_cls(
                key=self.uuri.get_libcloud_project_folder(),
            )
        elif self.uuri.scheme == "minio-libcloud":
            driver_cls = get_driver(Provider.MINIO)
            driver = driver_cls(
                key=self.uuri.user,
                secret=self.uuri.password,
                secure=True,
                host=self.uuri.get_host(),
                port=self.uuri.get_port(),
            )
        elif self.uuri.scheme == "gcs-libcloud":
            cls = get_driver(Provider.GOOGLE_STORAGE)
            driver = cls(
                key=self.uuri.user,
                secret=self.uuri.password,
                project=self.uuri.netloc,
            )
        elif self.uuri.scheme == "azure-libcloud":
            cls = get_driver(Provider.AZURE_BLOBS)
            driver = cls(
                key=self.uuri.user,
                secret=self.uuri.password,
            )
        else:
            msg = f"Cannot initialize libcloud diver for unknown {self.uuri.scheme}"
            raise OSError(msg)
        try:
            for _ in driver.iterate_containers():
                break
        except (
            ConnectionRefusedError,
            requests.exceptions.ConnectionError,
            libcloud.common.types.InvalidCredsError,
            AttributeError,
        ) as e:
            driver = None
            msg = f"Could not connect to server: {e}"
            logger.warning(msg)
        return driver

    @property
    def object(self) -> Object:
        """Get the libcloud object associated with this file.

        Returns:
            The libcloud object, or None if not found.
        """
        return self.get_object()

    def container_exists(self, container_name: str | None = None) -> bool:
        """Check if a container exists in the storage.

        Args:
            container_name: Name of the container to check. Defaults to self.uuri.get_container_name().

        Returns:
            True if the container exists, otherwise False.
        """
        if container_name is None:
            container_name = self.uuri.get_container_name()
        available_containers = []
        try:
            available_containers = [c.name for c in self.driver.list_containers()]
        except (
            requests.exceptions.ConnectionError,
            libcloud.common.types.InvalidCredsError,
        ):
            msg = f"Cannot connect to {self.uuri.scheme}://{self.uuri.get_host()}:{self.uuri.get_port()}."
            logger.warning(msg)
        except AttributeError:
            logger.warning("Driver was not initialized!")
        return container_name in available_containers

    def remote_object_exists(
        self,
        object_name: str | None = None,
    ) -> bool:
        """Check if an object exists in the container.

        Args:
            object_name: Name of the object to check. Defaults to self.uuri.get_object_name().

        Returns:
            True if the object exists, otherwise False.
        """
        answer = False
        if object_name is None:
            object_name = self.uuri.get_object_name()
        if self.container_exists() is True:
            container = self.get_container()
            available_objects = [o.name for o in container.list_objects()]
            answer = object_name in available_objects
        return answer

    def create_container(self, container_name: str | None = None) -> None:
        """Create a container or bucket if it does not exist.

        Args:
            container_name: Name of the container to create. Defaults to self.uuri.get_container_name().
        """
        if container_name is None:
            container_name = self.uuri.get_container_name()
        if self.container_exists() is False:
            self.driver.create_container(container_name=container_name)

    def get_container(
        self,
        container_name: str | None = None,
    ) -> libcloud.base.ContainerProvider:
        """Get the container instance.

        Args:
            container_name: Name of the container. Defaults to self.uuri.get_container_name().

        Returns:
            The libcloud container object.
        """
        if container_name is None:
            container_name = self.uuri.get_container_name()
        if self._container is None:
            if self.container_exists() is False:
                self.create_container()
            self._container = self.driver.get_container(container_name=container_name)
        return self._container

    def list_container_items(
        self,
        container_name: str | None = None,
        pattern: str | None = None,
        full_string: bool = False,
    ) -> list:
        """List all objects in the container, optionally filtering by regex.

        Args:
            container_name: Name of the container. Defaults to self.uuri.get_container_name().
            pattern: Regex pattern for filtering object names.
            full_string: Whether to return the list with full strings or just fragments.

        Returns:
            List of object names after filtering.
        """
        if self._container is None:
            self.get_container(container_name=container_name)
        if full_string is True:
            container_objects = self.add_storage_uri_to_container_items(
                [obj.name for obj in self._container.list_objects()],
            )
        else:
            logger.warning(
                "DeprecationWarning: list_container_items with full_string=False will be deprecated soon, use full_string=True instead.",
            )
            container_objects = [obj.name for obj in self._container.list_objects()]
        if pattern is not None:
            container_objects = [
                name
                for name in container_objects
                if re.search(pattern, name) is not None
            ]
        return container_objects

    def get_object(
        self,
        container_name: str | None = None,
        object_name: str | None = None,
    ) -> libcloud.storage.base.Object | None:
        """Get a reference to the libcloud object for this file.

        Args:
            container_name: Name of the container.
            object_name: Name of the object.

        Returns:
            The libcloud object, or None if not found.
        """
        msg = f"Getting object reference for {self.uuri.get_object_name()}..."
        logger.debug(msg)
        if container_name is None:
            container_name = self.uuri.get_container_name()
        if object_name is None:
            object_name = self.uuri.get_object_name()
        if self._object is None:
            if self.container_exists() is False:
                try:
                    self.create_container(container_name=container_name)
                except (
                    libcloud.storage.types.InvalidContainerNameError,
                    libcloud.storage.types.ContainerAlreadyExistsError,
                ):
                    logger.info("Container already exits. Skipping creation.")
            try:
                container = self.get_container(container_name=container_name)
                self._object = container.get_object(object_name)
            except libcloud.storage.types.ObjectDoesNotExistError:
                logger.debug("Remote object does not exist")
        return self._object

    def download(self, overwrite_existing: bool = True) -> None:
        """Download remote object to local scratch directory.

        Args:
            overwrite_existing: If True, overwrite local file if it exists.
        """
        cloud_object = self.get_object()
        self.scratch_path.parent.mkdir(exist_ok=True)
        if cloud_object is not None:
            msg = f"Downloading into {self.uuri.get_libcloud_project_folder()}"
            logger.debug(msg)
            download_object = True
            if self.scratch_path.exists():
                local_hash = urgap.ucore.calculate_file_hash(
                    self.scratch_path,
                    hash_algorithm=urgap.config["hash_algorithm"],
                )
                if (
                    cloud_object.meta_data.get(
                        urgap.config["hash_algorithm"],
                        "we have no hash!! Seriously:)",
                    )
                    == local_hash
                ):
                    download_object = False
            if download_object is True:
                cloud_object.download(
                    str(self.scratch_path),
                    overwrite_existing=overwrite_existing,
                )
                msg = f"Downloaded {cloud_object.name} into {self.scratch_path.parent}"
                logger.debug(msg)
        else:
            logger.debug("Couldn't download - file not available")

    def upload(self, tags: dict | None = None) -> None:
        """Upload local file (and optional tags) to the object store.

        Args:
            tags: Optional dictionary of tags to upload.
        """
        if self.container_exists() is False:
            self.create_container()
        if self.uuri.scheme == "local-libcloud":
            self.upload_object_via_stream(
                local_file_obj=self.scratch_path,
                object_name=self.uuri.get_object_name(),
            )
            if tags is not None:
                with tempfile.NamedTemporaryFile(mode="w") as tmp_file:
                    json.dump(tags, tmp_file)
                    tmp_file.seek(0)
                    self.upload_object_via_stream(
                        local_file_obj=tmp_file.name,
                        object_name=self.uuri.get_object_name() + ".tag",
                    )
        else:
            self.upload_object_via_stream(
                local_file_obj=self.scratch_path,
                object_name=self.uuri.get_object_name(),
                extra={"meta_data": tags},
            )

    def upload_object_via_stream(
        self,
        local_file_obj: os.PathLike,
        object_name: str | None = None,
        extra: dict | None = None,
    ) -> None:
        """Upload a file stream to the remote object store.

        Args:
            local_file_obj: Path to the local file object.
            object_name: Name to use for the object in the container. If not provided, uses self.uuri.get_object_name().
            extra: Additional meta information to upload.
        """
        if object_name is None:
            object_name = self.uuri.get_object_name()
        if extra is None:
            logger.warning(">>>> No meta tags provided! <<<")
        container = self.get_container()
        msg = f"Uploading {local_file_obj} into {self.uuri.get_container_name()}#{self.uuri.get_object_name()}"
        logger.debug(msg)
        with local_file_obj.open("rb") as iterator:
            self.driver.upload_object_via_stream(
                iterator=iterator,
                container=container,
                object_name=object_name,
                extra=extra,
            )

    def remove_remote_object(self) -> None:
        """Delete the referenced remote file and its associated tag file (if present)."""
        if self.remote_object_exists():
            obj = self.get_object()
            self.driver.delete_object(obj)
            try:
                tag_obj_name = obj.name + ".tag"
                tag_obj = self.get_object(object_name=tag_obj_name)
                self.driver.delete_object(tag_obj)
            except libcloud.storage.types.ObjectDoesNotExistError:
                pass
