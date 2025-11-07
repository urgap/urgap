"""IOCreds submodule of urgap2."""

from typing import ParamSpec

P = ParamSpec("P")


class IOBaseCreds:
    """IOCreds Local class.

    All IOCreds classes inherit from this class.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new IOBaseCreds instance with secret_id attribute set from kwargs.

        Args:
            **kwargs: Used to set secret_id attribute from key.
        """
        self.secret_id = kwargs["secret_id"]

    def get_secret(self) -> None:
        """Get_secret method is implemented in subclass."""
        msg = "This needs to be implemented in the IOCreds class"
        raise NotImplementedError(msg)
