"""Env credentials subclass of urgap2's IOCreds submodule."""

import os

from typing import ParamSpec

from urgap.ucredentials.io._base import IOBaseCreds

P = ParamSpec("P")


class IOEnvCreds(IOBaseCreds):
    """IO class interface Env."""

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new IOEnvCreds class."""
        super().__init__(**kwargs)

    def get_secret(self) -> str:
        """Extract Secret from ENV for secret_id.

        Returns:
            Name of secret or better its known ID or None if no secret_id in ENV.
        """
        return os.environ.get(self.secret_id, None)