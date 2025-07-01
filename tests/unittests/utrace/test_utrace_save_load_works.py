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
def test_init_right_number_of_output_files(
    check_if_meta_interface_backend_is_available,
):
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
    ut.set_start_time()
    ut.set_stop_time(skipped=False)
    ut.save_umeta_information()
    storage_base_uri = ut.input_files[0].storage_base_uri
    ut2 = urgap.UTrace.load_from_umeta(
        wid=wid,
        storage_base_uri=storage_base_uri,
        umeta_io=io,
    )
    assert ut2.id == ut.id