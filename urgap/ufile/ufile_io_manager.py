"""UFileIOManager module of urgap."""

from urgap.ufile.io._base import UIOBase
from urgap.umanager import UManager


class UFileIOManager(UManager[UIOBase]):
    """Manager for UFile IO backends.

    The UFileIOManager is responsible for detecting and managing which IO classes
    are available for UFile objects, mapping storage schemes to their respective implementations.
    """

    NAMESPACE_PACKAGE = "urgap.ufile.io"
    MARKER_ATTR = "SCHEMA"
    BASE_CLASS = UIOBase
