
from pathlib import Path
from typing import ParamSpec


P = ParamSpec("P")


class UIOBase:

    provide a consistent interface for working with local copies of files.
    """

    reported_tmp_files = set()

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create a new UIOBase instance and set the uuri attribute from kwargs.

        Args:
            kwargs: Must include "uuri", which is the parsed UUri object.
        """
        self.uuri = kwargs["uuri"]

    @property
    def scratch_path(self) -> Path:
        """Get the full local file path for the scratch file.

        The parent directory is created if it doesn't exist.

        Returns:
            The Path object pointing to the file on the local scratch disk.
        """
        _scratch_path = (
            / self.uuri.get_container_name()
            / self.uuri.get_object_name()
        ).resolve()
        _scratch_path.parent.mkdir(exist_ok=True, parents=True)

        return _scratch_path

    def download(self) -> None:
        """Download the file from remote storage to local scratch disk.

        This method must be implemented in a subclass for a specific storage backend.
        Raises NotImplementedError if not overridden.
        """
        msg = "This needs to be implemented in the UIO class"
        raise NotImplementedError(msg)

    def upload(self) -> None:
        """Upload the file from local scratch disk to remote storage.

        This method must be implemented in a subclass for a specific storage backend.
        Raises NotImplementedError if not overridden.
        """
        msg = "This needs to be implemented in the UIO class"
        raise NotImplementedError(msg)

    def local_object_exists(self) -> bool:
        """Check whether the local scratch file already exists.

        Returns:
            True if the file exists on disk, False otherwise.
        """
        return self.scratch_path.exists()