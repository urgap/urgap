import datetime
import json



def test_date_formats_are_converted_properly():
    L_date_obj = datetime.datetime.fromisoformat("2008-05-25T02:11:00.000000")

    history_entry = {
        "uname": "L!",
        "created": L_date_obj,
    }
    assert "2008-05-25T02:11:00" in h
    assert history_entry_recreated["created"] == L_date_obj


def test_list_of_UFiles_objects_are_converted_properly():
    payload = {"ufiles": [ufile_1, ufile_2]}
    assert ufile_1.as_uri() in h
    assert ufile_2.as_uri() in h
    assert payload["ufiles"] == [ufile_1, ufile_2]