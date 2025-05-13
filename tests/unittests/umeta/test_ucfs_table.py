import pytest



@pytest.mark.parametrize(
    "check_if_meta_interface_backend_is_available",
    [
        ("sqlite3", None),
    ],
    indirect=["check_if_meta_interface_backend_is_available"],
)
def test_read_write_user_dict(check_if_meta_interface_backend_is_available, tmp_dir):
    uf.rebase(f"file://{tmp_dir}/2/test", upload=True)