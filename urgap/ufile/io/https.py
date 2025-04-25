
import json
import logging
import urllib

from typing import ParamSpec

import requests



P = ParamSpec("P")


class IOHTTPS(UIOBase):

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new UIO class for processing https scheme.

        Args:
        """
        super().__init__(**kwargs)

    def get_remote_tags(self) -> dict | None:

        Returns:
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
        """

    def download(self) -> None:
        """Download referenced remote object.

        """
        try:

        except urllib.error.URLError:
            msg = (
                "[ - HTTP - ] For OSX, make sure that certificates are installed (/Applications/Python 3.x/Install Certificates.command)",
            )
            self.scratch_path.unlink()

    def upload(self, tags: dict | None = None) -> None:
        if tags is None:
        msg = "Cannot upload via https!"
        raise NotImplementedError(msg)

    def remote_object_exists(self) -> bool:
        """Verify referenced remote object exists.

        Returns:
        """
        try:
            exists = True
        except urllib.error.HTTPError:
            exists = False
        return exists