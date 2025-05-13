import pytest



@pytest.mark.parametrize(
    "check_if_meta_interface_backend_is_available",
    [
        ("sqlite3", None),
    ],
    indirect=["check_if_meta_interface_backend_is_available"],
)
def test_read_write_user_dict(check_if_meta_interface_backend_is_available, tmp_dir):
    uf.rebase(f"file://{tmp_dir}/1/test#unified_csvs1/demo.csv", upload=True)
    uf.rebase(f"file://{tmp_dir}/1/test#unified_csvs2/demo.csv", upload=True)
    uf.rebase(f"file://{tmp_dir}/1/test#unified_csvs3/demo.csv", upload=True)
    uf.rebase(f"file://{tmp_dir}/2/test", upload=True)

    filter_object_names = um.io.get_ucfs_object_name_info(
        storage_base_uri=f"file://{tmp_dir}/1/test",
        object_name="unified_csvs1/demo.csv",
    )
    all_storage_bases = [row.storage_base_uri for row in filter_object_names]
    assert len(all_storage_bases) == 1

        storage_base_uri=f"file://{tmp_dir}/1/test",
    )

    filter_storage_base_uri = um.io.get_ucfs_object_name_info(
    )
    all_storage_base_uri = [row.storage_base_uri for row in filter_storage_base_uri]
    assert len(all_storage_base_uri) == 3

    assert len(all_entries) == 0