"""IOCreds submodule of urgap."""

from abc import ABC, abstractmethod
from typing import ClassVar, ParamSpec

P = ParamSpec("P")


class IOBaseCreds(ABC):
    """All IOCreds classes inherit from this class."""

    SCHEME: ClassVar[str]

    def __init_subclass__(cls, *, abstract: bool = False, **kwargs: P.kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if abstract:
            return
        if not getattr(cls, "SCHEME", None):
            msg = f"{cls.__name__} must define a non-empty SCHEME class attribute."
            raise TypeError(msg)

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new IOBaseCreds instance with secret_id attribute set from kwargs.

        Args:
            **kwargs: Must include "secret_id".
        """
        if "secret_id" not in kwargs:
            msg = f"{type(self).__name__} requires 'secret_id'."
            raise TypeError(msg)
        self.secret_id = kwargs["secret_id"]

    @abstractmethod
    def get_secret(self) -> str | None:
        """Get_secret method is implemented in subclass."""
        raise NotImplementedError
