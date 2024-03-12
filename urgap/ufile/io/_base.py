
from pathlib import Path


class UIOBase:

    """

    reported_tmp_files = set()


        Args:
        """

    @property
        _scratch_path = (
        ).resolve()
        _scratch_path.parent.mkdir(exist_ok=True, parents=True)

        return _scratch_path



    def local_object_exists(self) -> bool:

        Returns:
        """
        return self.scratch_path.exists()