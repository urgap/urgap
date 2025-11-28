"""Mylabdata scheme subclass of urgap2's UIO submodule."""

import json
import logging
import re

from collections.abc import Callable
from typing import ParamSpec

import requests

import urgap

from urgap.ufile.io._base import UIOBase

P = ParamSpec("P")
logger = logging.getLogger(__name__)


def make_expiration_safe_request(func: Callable) -> requests.Response:
    """Perform a REST API request twice in case the token expired.

    If a request returns status code 403 (forbidden), the function will
    automatically re-authenticate and try again once.
    """

    def request_func_wrapper(
        self: urgap.UFile.io,
        *args: str,
        **kwargs: P.kwargs,
    ) -> requests.Response:
        response = func(self, *args, **kwargs)
        if (response is not None) and (response.status_code == 403):
            logger.warning("The API token seems to be invalid. Requesting new token.")
            self._get_token_bearer()
            response = func(self, *args, **kwargs)
        return response

    return request_func_wrapper


class IOMyLabData(UIOBase):
    """UIO class interface for mylabdata.

    Provides interaction with the mylabdata REST API for file upload, download, and metadata operations.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create a new UIO class for processing mylabdata.

        Args:
            **kwargs: Passed to UIOBase, contains uri and any configuration keys.
        """
        super().__init__(**kwargs)
        self._api_cert = urgap.config["certificates"].get(self.uuri.netloc, True)
        self._api_token = None
        self._get_token_bearer()

    @property
    def remote_path(self) -> str | None:
        """Get remote file path.

        Returns:
            None (remote path is handled via REST endpoints).
        """
        return None

    @property
    def remote_tag_path(self) -> str | None:
        """Get remote file tag path.

        Returns:
            None (remote tag path is handled via REST endpoints).
        """
        return None

    def _get_token_bearer(self) -> None:
        """Retrieve and cache the API access token ("bearer" token).

        Raises:
            ConnectionError: If the login attempt fails.
        """
        files_cred = {
            "userId": self.uuri.user,
            "password": self.uuri.password,
        }
        response = requests.post(
            url=self.uuri.get_mylabdata_api_url() + "/login",
            json=files_cred,
            verify=self._api_cert,
            timeout=(
                urgap.config.get("requests_timeout_connect", None),
                urgap.config.get("requests_timeout_read", None),
            ),
        )
        if response.status_code == 200:
            token = response.json()["data"]["token"]
            self._api_token = {"Authorization": f"Bearer {token}"}
        else:
            msg = f"Login failed with status code: {response.status_code}"
            logger.error(msg)
            raise ConnectionError(msg)

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with the referenced file.

        Returns:
            A dictionary of tags, or None if tags could not be retrieved.
        """
        tags = None
        url = (
            self.uuri.get_mylabdata_api_url_files()
            + self.uuri.path
            + "/"
            + self.uuri.fragment
            + ".tag"
        )
        response = requests.get(
            url=url,
            verify=self._api_cert,
            headers=self._api_token,
            timeout=(
                urgap.config.get("requests_timeout_connect", None),
                urgap.config.get("requests_timeout_read", None),
            ),
        )
        if response.status_code == 200:
            tags = json.loads(response.content)
        return tags

    @make_expiration_safe_request
    def upload(self, tags: dict | None = None) -> requests.Response:
        """Upload the local scratch file to the remote location.

        If tags are provided, they are also uploaded as a .tag file.

        Args:
            tags: Optional dictionary of tags/metadata to upload alongside the file.

        Returns:
            The HTTP response from the file upload request.

        Raises:
            ValueError: If upload fails (not HTTP 200 or 409).
        """
        url = self.uuri.mylabdata_url
        with self.scratch_path.open("rb") as file:
            response = requests.post(
                url=url,
                data=file,
                verify=self._api_cert,
                headers=self._api_token,
                timeout=(
                    urgap.config.get("requests_timeout_connect", None),
                    urgap.config.get("requests_timeout_read", None),
                ),
            )
        if response.status_code == 409:
            msg = f"File {self.scratch_path} already exists in remote location {url} , skipping upload"
            logger.info(msg)
        elif response.status_code == 200:
            msg = f"Uploaded file {self.scratch_path} to remote location {url}"
            logger.info(msg)
        else:
            msg = f"Uploading file {self.scratch_path} to remote location {url} failed with status code: {response.status_code}"
            logger.error(msg)
            raise ValueError(msg)
        if tags is not None:
            url += ".tag"
            tag_response = requests.post(
                url=url,
                data=json.dumps(tags).encode("utf-8"),
                verify=self._api_cert,
                headers=self._api_token,
                timeout=(
                    urgap.config.get("requests_timeout_connect", None),
                    urgap.config.get("requests_timeout_read", None),
                ),
            )
            if tag_response.status_code == 409:
                logger.info("Tag already exists, skipping upload")
            elif tag_response.status_code == 200:
                msg = f"Uploaded tag to remote location {url}"
                logger.info(msg)
            else:
                msg = (
                    f"Uploading tag failed with status code: {tag_response.status_code}"
                )
                logger.error(msg)
                raise ValueError(msg)
        return response

    @make_expiration_safe_request
    def download(self) -> requests.Response:
        """Download the file from remote storage to the local scratch path.

        Writes the file content to the local disk. Also attempts to retrieve tags.

        Returns:
            The HTTP response from the file download request.
        """
        url = self.uuri.mylabdata_url
        response = requests.get(
            url=url,
            verify=self._api_cert,
            headers=self._api_token,
            timeout=(
                urgap.config.get("requests_timeout_connect", None),
                urgap.config.get("requests_timeout_read", None),
            ),
            stream=True,
        )
        if response.status_code == 200:
            with self.scratch_path.open("wb") as file:
                for chunk in response.iter_content(8192):
                    if chunk:
                        file.write(chunk)
            url += ".tag"
            self.get_remote_tags()
        return response

    def list_container_items(
        self,
        pattern: str | None = None,
        limit: int = 1000,
        full_string: bool = False,
        with_hashes: bool = False,
    ) -> list:
        """Get objects in the folder/container, optionally filtered by a regex pattern.

        Args:
            pattern: Regex pattern for filtering object names.
            limit: Maximum number of files to request in one query.
            full_string: Whether to return the list with full strings or just fragments.

        Returns:
            List of object names matching the filter.
        """
        equip_task_id_fragment = self.uuri.path.split("/")[1:]
        equip_task_id_fragment.append(limit)
        query = urlencode(
            dict(
                zip(
                    (
                        "equipmentId",
                        "taskId",
                        "limit",
                    ),
                    equip_task_id_fragment,
                    strict=False,
                ),
            ),
        )
        url = self.uuri.get_mylabdata_api_url_files() + f"?{query}"
        response = requests.get(
            url=url,
            verify=self._api_cert,
            headers=self._api_token,
            timeout=(
                urgap.config.get("requests_timeout_connect", None),
                urgap.config.get("requests_timeout_read", None),
            ),
        )
        while len(response.json()["data"].get("nextPage", "")) != 0:
            response = requests.get(
                url=self.uuri.get_mylabdata_api_url()
                + response.json()["data"]["nextPage"],
                verify=self._api_cert,
                headers=self._api_token,
                timeout=(
                    urgap.config.get("requests_timeout_connect", None),
                    urgap.config.get("requests_timeout_read", None),
                ),
            )
        return container_objects

    def remote_object_exists(self) -> bool:
        """Check if the object exists in the container.

        Returns:
            True if the object exists, False otherwise.
        """
        return self.uuri.fragment in self.list_container_items()