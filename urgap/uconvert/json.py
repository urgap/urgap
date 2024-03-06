
import datetime
import json


# inspired by https://gist.github.com/simonw/7000493


class JSONEncoder(json.JSONEncoder):


        Args:

        Returns:
        """
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "UFile",
                "uri": obj.as_uri(),
            }
            d = {"_type": "UFileList", "uris": []}
            for x in obj:
                if x is None:
                    d["uris"].append(x)
                else:
                    d["uris"].append(x.as_uri())
            return d



class JSONDecoder(json.JSONDecoder):

            *args,
            object_hook=self.object_hook,
            **kwargs,
        )


        Args:

        Returns:
        """
                return datetime.datetime.fromisoformat(obj["value"])
                return set(obj["value"])