import pytest

import urgap


@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                f"test_node_data/test.txt",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "triggers_nuttin": 100,
                        "triggers_rerun": 100,
                        "triggers_rerun_-3": 100,
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                    },
                },
            ),
            ["TestNode1:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_works_with_args(provide_clean_test_node_dirs, tmp_dir):
    unodes, ufiles, urun_dict = provide_clean_test_node_dirs
    _output = unodes["TestNode1:1.0.0"].run(
        ufiles,
        urun_dict,
        storage_base_uri=f"file://{tmp_dir}/new_path",
    )
    assert _output[0].as_storage_base_uri() == f"file://{tmp_dir}/new_path"


@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                f"test_node_data/test.txt",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "triggers_nuttin": 100,
                        "triggers_rerun": 100,
                        "triggers_rerun_-3": 100,
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                    },
                },
            ),
            ["TestNode1:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_works_with_kwargs(provide_clean_test_node_dirs, tmp_dir):
    unodes, ufiles, urun_dict = provide_clean_test_node_dirs
    _output = unodes["TestNode1:1.0.0"].run(
        ufiles=ufiles,
        urun_dict=urun_dict,
        storage_base_uri=f"file://{tmp_dir}/new_path",
    )
    assert _output[0].as_storage_base_uri() == f"file://{tmp_dir}/new_path"


@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                f"test_node_data/test.txt",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "triggers_nuttin": 100,
                        "triggers_rerun": 100,
                        "triggers_rerun_-3": 100,
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                    },
                },
            ),
            ["TestNode1:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_works_with_mixture(provide_clean_test_node_dirs, tmp_dir):
    unodes, ufiles, urun_dict = provide_clean_test_node_dirs
    _output = unodes["TestNode1:1.0.0"].run(
        ufiles,
        urun_dict=urun_dict,
        storage_base_uri=f"file://{tmp_dir}/new_path",
    )
    assert _output[0].as_storage_base_uri() == f"file://{tmp_dir}/new_path"


@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                f"test_node_data/test.txt",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "triggers_nuttin": 100,
                        "triggers_rerun": 100,
                        "triggers_rerun_-3": 100,
                    },
                    "unode_parameters": {
                        "storage_base_uri": f"file://{urgap._test_folder}/definetlynothere",
                    },
                },
            ),
            ["TestNode1:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_works_with_overwrite(provide_clean_test_node_dirs, tmp_dir):
    unodes, ufiles, urun_dict = provide_clean_test_node_dirs
    _output = unodes["TestNode1:1.0.0"].run(
        ufiles=ufiles,
        urun_dict=urun_dict,
        storage_base_uri=f"file://{tmp_dir}/new_path",
    )
    assert _output[0].as_storage_base_uri() == f"file://{tmp_dir}/new_path"