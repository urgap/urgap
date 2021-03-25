import datetime
# inspired by https://gist.github.com/simonw/7000493


class JSONEncoder(json.JSONEncoder):

        if isinstance(obj, datetime.datetime):


class JSONDecoder(json.JSONDecoder):
            *args,
            object_hook=self.object_hook,
            **kwargs,
        )

                return datetime.datetime.fromisoformat(obj["value"])