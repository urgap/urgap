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
            [
                ),
        ),
        umeta_io=io,
    )
    ut.set_start_time()
    ut.set_stop_time(skipped=False)
    ut.save_umeta_information()
        wid=wid,
        umeta_io=io,
    )
    assert ut2.id == ut.id