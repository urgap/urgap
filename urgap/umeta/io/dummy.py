"""UMeta dummy class for designing additional UMeta interfaces."""

from ._base import UMetaIOBase


class UMeta(UMetaIOBase):
    """UMeta dummy class - always returning True and not storing any run time info! - ya welcome."""

    def __init__(self) -> None:
        """Needs to be implemented."""
        super().__init__()
        self.name = "UMeta for test purposes"

    def load(self) -> dict:
        """Needs to be implemented."""
        return {"history": [], "urun_dict": {}}

    def save(self, umeta: dict | None = None) -> None:
        """Needs to be implemented."""

    def umeta_exists(self) -> bool:
        """Needs to be implemented."""
        return False