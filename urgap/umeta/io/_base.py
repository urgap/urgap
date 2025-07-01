from __future__ import annotations

from copy import deepcopy


class UMetaIOBase:
    """UMetaIO Base Class.

    Base class for UMeta IO interfaces in urgap, which handle runtime metadata and history.

    Prior to the introduction of UMeta, .ujson files were created. With UMeta,
    any backend (such as MongoDB, PostgreSQL, etc.) can be used to persist this information.

    The UMeta interface is key to determining whether a node needs to be re-run,
    depending on an input file and the set of parameters.
    """

    def __init__(self) -> None:
        """Initialize UMetaIOBase."""
        self.name = "UMetaBase"

    def __deepcopy__(self, memo: dict) -> UMetaIOBase:
        """Create a deep copy of the UMeta information.

        Args:
            memo: The memoization dictionary passed by the `deepcopy` function.

        Note:
            Database connections, collections, and similar resources should be
            stored as private properties in subclasses and will not be serialized.

        Returns:
            A deep copy of the UMeta object.
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
        """Define how UMeta files are loaded in concrete subclasses."""
        raise NotImplementedError

    def save(self, umeta: UMetaIOBase | None = None) -> None:
        """Define how UMeta files are saved in concrete IO subclasses.

        Args:
            umeta: The UMeta object to save.
        """
        raise NotImplementedError

    def find_wid_members(self, wid: str, limit: int | None = None) -> None:
        """Find all UMeta entries associated with a given workflow ID (WID).

        Args:
            wid: The workflow ID to search for.
            limit: Optional maximum number of results.
        """
        raise NotImplementedError

        """Find all node execution IDs given an object name.

        Args:
            object_name: The object name to search for.
        """
        raise NotImplementedError

        self,
        object_name: str,
    ) -> list:
        """Find all producer node execution IDs given an object name.

        Args:
            object_name: The object name to search for.

        Returns:
            List of node execution IDs that produced the object.
        """
        raise NotImplementedError

        self,
        object_name: str,
    ) -> list:
        """Find all consumer node execution IDs given an object name.

        Args:
            object_name: The object name to search for.

        Returns:
            List of node execution IDs that consumed the object.
        """
        raise NotImplementedError

    def retrieve_interface_statistics(self) -> str:
        """Retrieve statistics about the UMeta IO interface.

        Returns:
            A string containing interface statistics.
        """
        raise NotImplementedError

    def find_last_processed_files(self) -> str:
        """Find the last processed files.

        Returns:
            Information about the last processed files.
        """
        raise NotImplementedError

        """Find details for a given node execution ID.

        Args:

        Returns:
            List of details for the given node execution ID.
        """
        raise NotImplementedError