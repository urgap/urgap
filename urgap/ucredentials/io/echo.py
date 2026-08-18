"""Env credentials subclass of urgap's IOCreds submodule."""

from typing import ParamSpec

from urgap.ucredentials.io._base import IOBaseCreds

P = ParamSpec("P")

class IOEchoCreds(IOBaseCreds):
    """IO class interface Echo."""
    
    SCHEME = "echo"

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new IOEchoCreds class."""
        super().__init__(**kwargs)

    def get_secret(self) -> str:
        """Echo secret_id as secret for testing.

        Returns:
            Name of secret or better its known ID.
        """
        return self.secret_id
