"""UMessageBusManager module of urgap."""

from urgap.umanager import UManager
from urgap.umessagebus.io._base import UMessageBusBase


class UMessageBusManager(UManager[UMessageBusBase]):
    """Manager for message bus transports.

    The UMessageBusManager detects which message bus implementations are
    available, mapping cred_key schemes to their respective implementations.
    """

    NAMESPACE_PACKAGE = "urgap.umessagebus.io"
    MARKER_ATTR = "SCHEMA"
    BASE_CLASS = UMessageBusBase
