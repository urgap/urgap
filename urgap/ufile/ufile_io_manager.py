"""UFileIOManager module of urgap."""

import contextlib
import importlib
import inspect
import pkgutil


class UFileIOManager:
    """Manager for UFile IO backends.

    The UFileIOManager is responsible for detecting and managing which IO classes
    are available for UFile objects, mapping storage schemes to their respective implementations.
    Backends are discovered dynamically from the urgap.ufile.io namespace package, enabling
    third-party packages to register additional backends by installing modules into that namespace.
    """

    def __init__(self) -> None:
        """Initialize the UFile IO Manager.

        Scans the urgap.ufile.io namespace for modules that declare a SCHEMA constant and
        contain a UIOBase subclass, then registers them in self.available_io_classes.
        """
        super().__init__()
        self.available_io_classes = {}
        self._discover_io_backends()

    def _discover_io_backends(self) -> None:
        """Discover and register all IO backend modules in the urgap.ufile.io namespace."""
        import urgap.ufile.io as io_namespace

        from urgap.ufile.io._base import UIOBase

        for _finder, module_name, _is_pkg in pkgutil.iter_modules(
            io_namespace.__path__,
            prefix="urgap.ufile.io.",
        ):
            short_name = module_name.rsplit(".", 1)[-1]
            if short_name.startswith("_"):
                continue
            with contextlib.suppress(ImportError):
                module = importlib.import_module(module_name)
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, UIOBase)
                        and obj is not UIOBase
                        and obj.__module__ == module_name
                        and obj.SCHEMA is not None
                    ):
                        self.available_io_classes[obj.SCHEMA] = obj
