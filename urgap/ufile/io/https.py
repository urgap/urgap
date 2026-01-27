"""HTTPS scheme subclass of urgap2's UIO submodule."""

import json
import logging
import urllib

from typing import ParamSpec

import requests

import urgap

from urgap.ufile.io._base import UIOBase

P = ParamSpec("P")
logger = logging.getLogger(__name__)


class IOHTTPS(UIOBase):
    """UIO Class interface for http/https file objects.

    Handles interaction with files accessible via HTTP/S URLs, including download and tag retrieval.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new UIO class for processing https scheme.

        Args:
            **kwargs: Requires 'uuri' key to set respective attribute.
        """
        super().__init__(**kwargs)

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with the referenced file.

        Returns:
            A dictionary containing remotely stored tags, or None if unavailable or decoding fails.
        """
        tags = None
        response = requests.get(
            self.uuri.get_https_remote_tag_path(),
            timeout=(
                urgap.config.get("requests_timeout_connect", None),
                urgap.config.get("requests_timeout_read", None),
            ),
        )
        if response.status_code == 200:
            try:
                tags = response.json()
            except json.decoder.JSONDecodeError:
                msg = f"Connection to {self.uuri.get_https_remote_tag_path()} seems to be OK, but cannot receive tags!"
                logger.warning(msg)
        return tags

    def get_object(self) -> str:
        """Get referenced URL.

        Returns:
            The remote URL as a string.
        """
        return self.uuri.get_https_remote_path()

    def download(self) -> None:
        """Download referenced remote object.

        Writes the remote object to the local scratch path.
        If download fails, removes the partially downloaded file.
        """
        try:
            with self.scratch_path.open("wb"):
                urllib.request.urlretrieve(
                    self.uuri.get_https_remote_path(),
                    filename=self.scratch_path,
                )

        except urllib.error.URLError:
            msg = (
                f"[ - HTTP - ] WARNING! Could not download {self.uuri.get_https_remote_path()} Check your internet connection!",
                "[ - HTTP - ] For OSX, make sure that certificates are installed (/Applications/Python 3.x/Install Certificates.command)",
            )
            logger.warning(msg)
            self.scratch_path.unlink()

    def upload(self, tags: dict | None = None) -> None:
        """Upload method unsupported for https.

        Args:
            tags: Tags to write to remote location (ignored).

        Raises:
            NotImplementedError: Always raised, as HTTP/S does not support upload.
        """
        if tags is None:
            logger.warning("No tags provided, skipping upload.")
        msg = "Cannot upload via https!"
        raise NotImplementedError(msg)

    def remote_object_exists(self) -> bool:
        """Verify referenced remote object exists.

        Returns:
            True if the remote object exists, otherwise False.
        """
        try:
            urllib.request.urlretrieve(
                self.uuri.get_https_remote_path(),
                filename=self.scratch_path,
            )
            exists = True
        except urllib.error.HTTPError:
            exists = False
        return exists
