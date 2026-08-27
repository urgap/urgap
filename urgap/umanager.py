"""Generic registry-based manager for Urgap plugin-style backends."""

import inspect
import logging

from typing import ClassVar, Generic, TypeVar

from urgap.util import iter_public_modules

logger = logging.getLogger(__name__)

T = TypeVar("T")


def discover_backend_classes(
    namespace_package: str,
    base_class: type[T],
    marker_attr: str,
) -> dict[str, type[T]]:
    """Scan a namespace package for base_class subclasses, keyed by marker_attr."""
    registry: dict[str, type[T]] = {}
    for module in iter_public_modules(namespace_package):
        for _, obj in inspect.getmembers(module, inspect.isclass):
            marker_value = getattr(obj, marker_attr, None)
            if (
                issubclass(obj, base_class)
                and obj is not base_class
                and obj.__module__ == module.__name__
                and marker_value
            ):
                if marker_value in registry:
                    msg = (
                        f"Duplicate backend registration for {marker_value!r}: "
                        f"{registry[marker_value]} and {obj}"
                    )
                    raise ValueError(msg)
                registry[marker_value] = obj
    return registry


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
        if not self.available_classes:
            logger.warning(
                "No %s backends discovered in '%s'.",
                self.BASE_CLASS.__name__,
                self.NAMESPACE_PACKAGE,
            )

    @property
    def available_io_classes(self) -> dict[str, type[T]]:
        """Alias for available_classes."""
        return self.available_classes
