from datetime import datetime

import pytest



@pytest.mark.parametrize(
    "check_if_meta_interface_backend_is_available",
    [
        ("sqlite3", None),
    ],
    indirect=["check_if_meta_interface_backend_is_available"],
)
def test_read_write_user_dict(check_if_meta_interface_backend_is_available):
    io, url = check_if_meta_interface_backend_is_available
            [
                    f"/sequence_defghij.csv",
                ),
            ],
        ),
        umeta_io=io,
    )
    ut.urun_dict.user_dict["test"] = "u_fresh_cookies_stuff_young_bears"
    ut.start_time = datetime.now().astimezone()
    ut.duration_seconds = 1
    print(ut.urun_dict.user_dict, io, "<<<")
    ut.save_umeta_information()
    storage_base_uri = ut.input_files[0].storage_base_uri
        wid=wid,
        umeta_io=io,
        storage_base_uri=storage_base_uri,
    )

        "test": "u_fresh_cookies_stuff_young_bears",
    }