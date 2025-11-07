"""JSON handlers for urgap 2."""

from __future__ import annotations

import datetime
import json
import pathlib

from typing import ParamSpec

import urgap

P = ParamSpec("P")
# inspired by https://gist.github.com/simonw/7000493


class JSONEncoder(json.JSONEncoder):
    """Custom JSONEncoder class for urgap2 objects."""

    def default(
        self,
        obj: (
            datetime.datetime | set | urgap.UFile | pathlib.PosixPath | urgap.UFileList
        ),
    ) -> dict:
        """Serialize additional urgap and built-in types.

        Args:
            obj: Object to serialize.

        Returns:
            JSON-serializable dict or object.
        """
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.isoformat(),
            }
        if isinstance(obj, set):
            return {
                "_type": "set",
                "value": list(obj),
            }
        if isinstance(obj, urgap.UFile):
            return {
                "_type": "UFile",
                "uri": obj.as_uri(),
            }
        if isinstance(obj, pathlib.PosixPath):
            return {
                "_type": "Path",
                "value": str(obj),
            }
        if isinstance(obj, urgap.ufile_list.UFileList):
            d = {"_type": "UFileList", "uris": []}
            for x in obj:
                if x is None:
                    d["uris"].append(x)
                else:
                    d["uris"].append(x.as_uri())
            return d

        return obj


class JSONDecoder(json.JSONDecoder):
    """Custom JSONDecoder class for urgap2 objects."""

    def __init__(self, *args: str, **kwargs: P.kwargs) -> None:
        """Initialize with object_hook for urgap types."""
        super().__init__(
            *args,
            object_hook=self.object_hook,
            **kwargs,
        )

    def object_hook(
        self,
        obj: dict,
    ) -> dict | datetime.datetime | set | pathlib.Path | urgap.UFile | urgap.UFileList:
        """Decode urgap-specific objects from dicts.

        Args:
            obj: Dict to decode.

        Returns:
            Decoded object or original dict.
        """
        if "_type" not in obj:
            return obj
        match obj["_type"]:
            case "datetime":
                return datetime.datetime.fromisoformat(obj["value"])
            case "set":
                return set(obj["value"])
            case "Path":
                return pathlib.Path(obj["value"])
            case "UFile":
                return urgap.UFile(obj["uri"])
            case "UFileList":
                uri_list = [
                    urgap.UFile(uri) if uri is not None else uri for uri in obj["uris"]
                ]
                return urgap.ufile_list.UFileList(uri_list)
