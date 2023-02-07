import pytest



@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            ),
                {
                    "parameters": {
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                    },
            ),
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs