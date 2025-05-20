
import ast
import getpass
import logging





    parses them, and provides helpers to access the elements as a dict.
    It also extracts tags from queries and can handle different storage backends.
    """

        self._user = None
        self._password = None
    def _get_credentials(self) -> None:

        """
        if self.scheme not in ("file", "https"):
            try:
                )
                msg = f"Set credentials for {credentials['user']}"
            except KeyError:
                credentials = {"user": getpass.getuser(), "password": None}
            self._user = credentials["user"]
            self._password = credentials["password"]

