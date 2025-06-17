
import json
import logging
import re

from collections.abc import Callable
from typing import ParamSpec

import requests



P = ParamSpec("P")


def make_expiration_safe_request(func: Callable) -> requests.Response:
    """Perform a REST API request twice in case the token expired.

    If a request returns status code 403 (forbidden), the function will
    automatically re-authenticate and try again once.
    """

    def request_func_wrapper(
        *args: str,
        **kwargs: P.kwargs,
    ) -> requests.Response:
        response = func(self, *args, **kwargs)
        if (response is not None) and (response.status_code == 403):
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
            json=files_cred,
            verify=self._api_cert,
            timeout=(
            ),
        )
        if response.status_code == 200:
            token = response.json()["data"]["token"]
            self._api_token = {"Authorization": f"Bearer {token}"}
        else:
            msg = f"Login failed with status code: {response.status_code}"
            raise ConnectionError(msg)

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with the referenced file.

        Returns:
            A dictionary of tags, or None if tags could not be retrieved.
        """
        tags = None
        url = (
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
        with self.scratch_path.open("rb") as file:
            response = requests.post(
                url=url,
                verify=self._api_cert,
                headers=self._api_token,
                timeout=(
                ),
            )
        if response.status_code == 409:
        elif response.status_code == 200:
        else:
            raise ValueError(msg)
        if tags is not None:
            url += ".tag"
            tag_response = requests.post(
                url=url,
                data=json.dumps(tags).encode("utf-8"),
                verify=self._api_cert,
                headers=self._api_token,
                timeout=(
                ),
            )
            if tag_response.status_code == 409:
            elif tag_response.status_code == 200:
                msg = f"Uploaded tag to remote location {url}"
            else:
                msg = (
                    f"Uploading tag failed with status code: {tag_response.status_code}"
                )
                raise ValueError(msg)
        return response

    @make_expiration_safe_request
    def download(self) -> requests.Response:
        """Download the file from remote storage to the local scratch path.

        Writes the file content to the local disk. Also attempts to retrieve tags.

        Returns:
            The HTTP response from the file download request.
        """
        response = requests.get(
            url=url,
            verify=self._api_cert,
            headers=self._api_token,
            timeout=(
            ),
        )
        if response.status_code == 200:
            with self.scratch_path.open("wb") as file:
            url += ".tag"
            self.get_remote_tags()
        return response

    def list_container_items(
        self,
        pattern: str | None = None,
        limit: int = 1000,
    ) -> list:
        """Get objects in the folder/container, optionally filtered by a regex pattern.

        Args:
            pattern: Regex pattern for filtering object names.
            limit: Maximum number of files to request in one query.

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
        response = requests.get(
            url=url,
            verify=self._api_cert,
            headers=self._api_token,
            timeout=(
            ),
        )
        while len(response.json()["data"].get("nextPage", "")) != 0:
            response = requests.get(
                verify=self._api_cert,
                headers=self._api_token,
                timeout=(
                ),
            )
        return container_objects

    def remote_object_exists(self) -> bool:
        """Check if the object exists in the container.

        Returns:
            True if the object exists, False otherwise.
        """
        return self.uuri.fragment in self.list_container_items()