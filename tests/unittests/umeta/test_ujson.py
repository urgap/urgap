import json
import pathlib

from datetime import datetime

import pytest

import urgap

from urgap.uconvert import json as urgap_json


@pytest.mark.parametrize(
    "check_if_meta_interface_backend_is_available",
    [
        ("sqlite3", None),
        ("postgresql", urgap.config["umeta-postgresql-url"]),
    ],
    indirect=["check_if_meta_interface_backend_is_available"],
)
def test_read_write_user_dict(check_if_meta_interface_backend_is_available):
    io, url = check_if_meta_interface_backend_is_available
    ut = urgap.UTrace(
        urun_dict=urgap.URunDict(),
        input_files=urgap.UFileList(
            [
                urgap.UFile(
                    uri=f"file://{urgap._test_folder}/data?uftype="
                    f"{urgap.uftypes.test.TEST_FILE1}#csvs"
                    f"/sequence_defghij.csv",
                ),
            ],
        ),
        unode_meta=urgap.init_node("TestNode1:1.0.0").META_INFO,
        umeta_io=io,
    )
    ut.urun_dict.user_dict["test"] = "u_fresh_cookies_stuff_young_bears"
    ut.start_time = datetime.now().astimezone()
    ut.duration_seconds = 1
    print(ut.urun_dict.user_dict, io, "<<<")
    ut.save_umeta_information()
    storage_base_uri = ut.input_files[0].storage_base_uri
    ut2 = urgap.UTrace.load_from_umeta(
        wid=wid,
        umeta_io=io,
        storage_base_uri=storage_base_uri,
    )

        "test": "u_fresh_cookies_stuff_young_bears",
    }


def test_json_encoder_encodes_set():
    data = {1, 2, 3}
    encoded = json.dumps(data, cls=urgap_json.JSONEncoder)
    decoded = json.loads(encoded, cls=urgap_json.JSONDecoder)

    assert decoded == data


def test_json_encoder_handles_ufilelist_with_none_mock():
    class DummyUFileList(list):
        pass

    ufile1 = urgap.UFile(uri="file://dummy/path1")
    ulist = DummyUFileList([ufile1, None])

    encoded = json.dumps(ulist, cls=urgap_json.JSONEncoder)

    decoded = json.loads(encoded, cls=urgap_json.JSONDecoder)

    assert isinstance(decoded[0], urgap.UFile)
    assert decoded[0].as_uri() == "file://dummy/path1"
    assert decoded[1] is None


def test_json_encoder_ufilelist_with_real_and_none():
    class DummyUFileList(list):
        pass

    ufile1 = urgap.UFile(uri="file://dummy/path1")
    ulist = DummyUFileList([None, ufile1])

    encoded = json.dumps(ulist, cls=urgap_json.JSONEncoder)

    decoded = json.loads(encoded, cls=urgap_json.JSONDecoder)

    assert decoded[0] is None

    assert isinstance(decoded[1], urgap.UFile)
    assert decoded[1].as_uri() == "file://dummy/path1"


def test_json_encoder_decoder_fallback():
    obj = 42

    encoded = json.dumps({"value": obj}, cls=urgap_json.JSONEncoder)

    decoded = json.loads(encoded, cls=urgap_json.JSONDecoder)

    assert decoded["value"] == obj


def test_json_decoder_cases():
    dt_obj = {"_type": "datetime", "value": "2025-08-20T12:34:56"}
    decoded_dt = json.loads(json.dumps(dt_obj), cls=urgap_json.JSONDecoder)
    assert isinstance(decoded_dt, datetime)
    assert decoded_dt.isoformat() == dt_obj["value"]

    set_obj = {"_type": "set", "value": [1, 2, 3]}
    decoded_set = json.loads(json.dumps(set_obj), cls=urgap_json.JSONDecoder)
    assert decoded_set == {1, 2, 3}

    path_obj = {"_type": "Path", "value": "/tmp/test"}
    decoded_path = json.loads(json.dumps(path_obj), cls=urgap_json.JSONDecoder)
    assert isinstance(decoded_path, pathlib.Path)
    assert str(decoded_path) == "/tmp/test"

    ufile_obj = {"_type": "UFile", "uri": "file://dummy/path"}
    decoded_ufile = json.loads(json.dumps(ufile_obj), cls=urgap_json.JSONDecoder)
    assert isinstance(decoded_ufile, urgap.UFile)
    assert decoded_ufile.as_uri() == "file://dummy/path"

    ufilelist_obj = {
        "_type": "UFileList",
        "uris": ["file://dummy/path1", "file://dummy/path2"],
    }
    decoded_ufilelist = json.loads(
        json.dumps(ufilelist_obj), cls=urgap_json.JSONDecoder
    )
    assert isinstance(decoded_ufilelist, urgap.ufile_list.UFileList)
    assert all(isinstance(x, urgap.UFile) for x in decoded_ufilelist)
    assert [x.as_uri() for x in decoded_ufilelist] == [
        "file://dummy/path1",
        "file://dummy/path2",
    ]