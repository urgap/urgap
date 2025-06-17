
from __future__ import annotations

import datetime
import json
import pathlib

from typing import ParamSpec


P = ParamSpec("P")
# inspired by https://gist.github.com/simonw/7000493


class JSONEncoder(json.JSONEncoder):

    def default(
        self,
        obj: (
        ),
    ) -> dict:

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
            return {
                "_type": "UFile",
                "uri": obj.as_uri(),
            }
        if isinstance(obj, pathlib.PosixPath):
            return {
                "_type": "Path",
                "value": str(obj),
            }
            d = {"_type": "UFileList", "uris": []}
            for x in obj:
                if x is None:
                    d["uris"].append(x)
                else:
                    d["uris"].append(x.as_uri())
            return d

        return obj


class JSONDecoder(json.JSONDecoder):

    def __init__(self, *args: str, **kwargs: P.kwargs) -> None:
        super().__init__(
            *args,
            object_hook=self.object_hook,
            **kwargs,
        )

    def object_hook(
        self,
        obj: dict,

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
            case "UFileList":
                uri_list = [
                ]