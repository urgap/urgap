import pytest

import urgap


# TODO: Something we need to fix. Maybe two different rebases. One user-facing, one internal.
@pytest.mark.skip
@pytest.mark.parametrize(
    "check_if_meta_interface_backend_is_available",
    [
        ("sqlite3", None),
        ("postgresql", urgap.config["umeta-postgresql-url"]),
    ],
    indirect=["check_if_meta_interface_backend_is_available"],
)
def test_read_write_user_dict(check_if_meta_interface_backend_is_available, tmp_dir):
    uf = urgap.UFile(uri=f"file://{urgap._test_folder}/data#unified_csvs/demo.csv")
    uf.rebase(f"file://{tmp_dir}/1/test#unified_csvs1/demo.csv", upload=True)
    uf.rebase(f"file://{tmp_dir}/1/test#unified_csvs2/demo.csv", upload=True)
    uf.rebase(f"file://{tmp_dir}/1/test#unified_csvs3/demo.csv", upload=True)
    uf.rebase(f"file://{tmp_dir}/2/test", upload=True)

    um = urgap.UMeta()
    filter_object_names = um.io.get_ucfs_object_name_info(
        storage_base_uri=f"file://{tmp_dir}/1/test",
        object_name="unified_csvs1/demo.csv",
    )
    all_storage_bases = [row.storage_base_uri for row in filter_object_names]
    assert len(all_storage_bases) == 1

    filter_ucfs = um.io.get_ucfs_object_name_info(
        storage_base_uri=f"file://{tmp_dir}/1/test",
        ucfs="unified_csvs1/demo.csv@16c0cea811a829ae630bb6559508e82c",
    )
    all_ucfs = [row.ucfs for row in filter_ucfs]
    assert len(all_ucfs) == 1

    filter_storage_base_uri = um.io.get_ucfs_object_name_info(
        storage_base_uri=f"file://{tmp_dir}/1/test",
    )
    all_storage_base_uri = [row.storage_base_uri for row in filter_storage_base_uri]
    assert len(all_storage_base_uri) == 3

    filter_none = um.io.get_ucfs_object_name_info(ucfs="nothing")
    all_entries = [row.ucfs for row in filter_none]
    assert len(all_entries) == 0
