
import json
import logging
import urllib

from typing import ParamSpec

import requests



P = ParamSpec("P")


class IOHTTPS(UIOBase):
    """UIO Class interface for http/https file objects.

    Handles interaction with files accessible via HTTP/S URLs, including download and tag retrieval.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new UIO class for processing https scheme.

        Args:
        """
        super().__init__(**kwargs)

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with the referenced file.

        Returns:
            A dictionary containing remotely stored tags, or None if unavailable or decoding fails.
        """
        tags = None
        response = requests.get(
            timeout=(
            ),
        )
        if response.status_code == 200:
            try:
                tags = response.json()
            except json.decoder.JSONDecodeError:
        return tags

    def get_object(self) -> str:
        """Get referenced URL.

        Returns:
            The remote URL as a string.
        """

    def download(self) -> None:
        """Download referenced remote object.

        Writes the remote object to the local scratch path.
        If download fails, removes the partially downloaded file.
        """
        try:

        except urllib.error.URLError:
            msg = (
                "[ - HTTP - ] For OSX, make sure that certificates are installed (/Applications/Python 3.x/Install Certificates.command)",
            )
            self.scratch_path.unlink()

    def upload(self, tags: dict | None = None) -> None:
        """Upload method unsupported for https.

        Args:
            tags: Tags to write to remote location (ignored).

        Raises:
            NotImplementedError: Always raised, as HTTP/S does not support upload.
        """
        if tags is None:
        msg = "Cannot upload via https!"
        raise NotImplementedError(msg)

    def remote_object_exists(self) -> bool:
        """Verify referenced remote object exists.

        Returns:
            True if the remote object exists, otherwise False.
        """
        try:
            exists = True
        except urllib.error.HTTPError:
            exists = False
        return exists