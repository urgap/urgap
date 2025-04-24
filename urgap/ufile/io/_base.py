
from pathlib import Path



class UIOBase:

    """

    reported_tmp_files = set()


        Args:
        """

    @property
    def scratch_path(self) -> Path:
        _scratch_path = (
        ).resolve()
        _scratch_path.parent.mkdir(exist_ok=True, parents=True)

        return _scratch_path

    def download(self) -> None:
        msg = "This needs to be implemented in the UIO class"
        raise NotImplementedError(msg)

        msg = "This needs to be implemented in the UIO class"
        raise NotImplementedError(msg)

    def local_object_exists(self) -> bool:

        Returns:
        """
        return self.scratch_path.exists()