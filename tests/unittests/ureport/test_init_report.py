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
def test_init_right_number_of_output_files(
    check_if_meta_interface_backend_is_available,
):
    io, url = check_if_meta_interface_backend_is_available
    urd = urgap.URunDict()
    wid = urd.wid
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.test.TEST_FILE1}#csvs"
                f"/sequence_defghij.csv",
            ),
        ],
    )
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=ufiles,
        unode_meta=urgap.init_node("TestNode1:1.0.0").META_INFO,
        umeta_io=io,
    )
    ut.start_time = datetime.now().astimezone()
    ut.duration_seconds = 42
    ut.save_umeta_information()
    ut_pac_id, ut_wid = ut.id

    ut2 = urgap.UTrace(
        urun_dict=urd,
        input_files=ufiles,
        unode_meta=urgap.init_node("TestNode2:1.0.0").META_INFO,
        umeta_io=io,
    )
    ut2.start_time = datetime.now().astimezone()
    ut2.duration_seconds = 161
    ut2.save_umeta_information()
    ut2_pac_id, ut2_wid = ut2.id

    ur = urgap.UReport(wid=wid, umeta_io=io)
    assert len(ur.execution_history) == 2
    assert {entry[0] for entry in ur.execution_history} == set(
        [ut_pac_id, ut2_pac_id],
    )
    assert {entry[1] for entry in ur.execution_history} == set([wid])
