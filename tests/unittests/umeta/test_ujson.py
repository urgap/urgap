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
                ),
        ),
        umeta_io=io,
    )
    ut.urun_dict.user_dict["test"] = "u_fresh_cookies_stuff_young_bears"
    print(ut.urun_dict.user_dict, io, "<<<")
    ut.save_umeta_information()
