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
            ),
    )
        urun_dict=urd,
        input_files=ufiles,
        umeta_io=io,
    )
    ut.save_umeta_information()

        urun_dict=urd,
        input_files=ufiles,
        umeta_io=io,
    )
    ut2.save_umeta_information()
