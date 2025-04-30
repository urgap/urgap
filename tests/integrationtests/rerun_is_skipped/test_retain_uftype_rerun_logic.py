import pytest



@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
                f"unified_csvs/BSA1_xtandem_alanine_unified.csv",
            ),
                {
                    "parameters": {
                        "FilterTabularToCSV:1.0.0": {
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                    },
            ),
            ["FilterTabularToCSV:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    retain_uftype = True