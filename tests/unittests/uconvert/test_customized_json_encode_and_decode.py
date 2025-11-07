import datetime
import json

import urgap


def test_date_formats_are_converted_properly():
    L_date_obj = datetime.datetime.fromisoformat("2008-05-25T02:11:00.000000")

    history_entry = {
        "uname": "L!",
        "created": L_date_obj,
    }
    h = json.dumps(history_entry, cls=urgap.uconvert.JSONEncoder)
    assert "2008-05-25T02:11:00" in h
    history_entry_recreated = json.loads(h, cls=urgap.uconvert.JSONDecoder)
    assert history_entry_recreated["created"] == L_date_obj


def test_list_of_UFiles_objects_are_converted_properly():
    ufile_1 = urgap.UFile(uri="file:///Heishiro/Mitsurugi/Do/not/forget#this/name")
    ufile_2 = urgap.UFile(uri="file:///I/will/give/you/a/taste/of#true/battle")
    payload = {"ufiles": [ufile_1, ufile_2]}
    h = json.dumps(payload, cls=urgap.uconvert.JSONEncoder)
    assert ufile_1.as_uri() in h
    assert ufile_2.as_uri() in h
    json.loads(h, cls=urgap.uconvert.JSONDecoder)
    assert payload["ufiles"] == [ufile_1, ufile_2]
