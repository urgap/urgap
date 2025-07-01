from datetime import datetime

import pytest

import urgap


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