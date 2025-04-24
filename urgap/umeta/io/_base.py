from __future__ import annotations

from copy import deepcopy


class UMetaIOBase:
    """UMetaIO Base Class.



    """

    def __init__(self) -> None:
        self.name = "UMetaBase"


        Args:

        Note:

        Returns:
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            setattr(result, k, deepcopy(v, memo))
        return result

    def load(self) -> None:
        raise NotImplementedError

        raise NotImplementedError

    def find_wid_members(self, wid: str, limit: int | None = None) -> None:
        raise NotImplementedError

        raise NotImplementedError

    ) -> list:

        Args:

        Returns:
        """
        raise NotImplementedError

    ) -> list:

        Args:

        Returns:
        """
        raise NotImplementedError

    def retrieve_interface_statistics(self) -> str:

        Returns:
        """

    def find_last_processed_files(self) -> str:


        Returns:
        """