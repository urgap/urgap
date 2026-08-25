"""Generic registry-based manager for Urgap plugin-style backends."""

import logging

from typing import ClassVar, Generic, TypeVar

from urgap.util import discover_backend_classes

logger = logging.getLogger(__name__)

T = TypeVar("T")


class UManager(Generic[T]):
    """Registry-backed manager: discovers backends and registers them by key."""

    NAMESPACE_PACKAGE: ClassVar[str]
    MARKER_ATTR: ClassVar[str]
    BASE_CLASS: ClassVar[type]

    def __init__(self) -> None:
        """Discover and register available implementations."""
        self.available_classes: dict[str, type[T]] = {}
        self._discover()

    def _discover(self) -> None:
        """Populate self.available_classes from the namespace package."""
        self.available_classes = discover_backend_classes(
            namespace_package=self.NAMESPACE_PACKAGE,
            base_class=self.BASE_CLASS,
            marker_attr=self.MARKER_ATTR,
        )

    @property
    def available_io_classes(self) -> dict[str, type[T]]:
        """Alias for available_classes."""
        return self.available_classes
