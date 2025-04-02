
import json
import logging
import urllib

import requests



class IOHTTPS(UIOBase):

        """Create new UIO class for processing https scheme.

        Args:
        """

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

        """Download referenced remote object.

        """
        try:

        except urllib.error.URLError:
                "[ - HTTP - ] For OSX, make sure that certificates are installed (/Applications/Python 3.x/Install Certificates.command)",
            )
            self.scratch_path.unlink()


    def remote_object_exists(self) -> bool:
        """Verify referenced remote object exists.

        Returns:
        """
        try:
            exists = True
        except urllib.error.HTTPError:
            exists = False
        return exists