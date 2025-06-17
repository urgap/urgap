from datetime import datetime

import pytest



@pytest.mark.parametrize(
    "check_if_meta_interface_backend_is_available",
    [
        ("sqlite3", None),
    ],
    indirect=["check_if_meta_interface_backend_is_available"],
)
def test_init_right_number_of_output_files(
    check_if_meta_interface_backend_is_available,
):
    io, url = check_if_meta_interface_backend_is_available
    wid = urd.wid
        [
                f"/sequence_defghij.csv",
            ),
        ],
    )
        urun_dict=urd,
        input_files=ufiles,
        umeta_io=io,
    )
    ut.start_time = datetime.now().astimezone()
    ut.duration_seconds = 42
    ut.save_umeta_information()

        urun_dict=urd,
        input_files=ufiles,
        umeta_io=io,
    )
    ut2.start_time = datetime.now().astimezone()
    ut2.duration_seconds = 161
    ut2.save_umeta_information()

    assert len(ur.execution_history) == 2
    assert {entry[0] for entry in ur.execution_history} == set(
    )
    assert {entry[1] for entry in ur.execution_history} == set([wid])