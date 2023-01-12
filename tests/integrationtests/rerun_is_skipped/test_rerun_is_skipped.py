import tempfile

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
def test_node_workflow_rerun_is_skipped_simple(provide_clean_test_node_dirs):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    with tempfile.TemporaryDirectory() as tmpdirname:


            ufiles=ufiles,
            urun_dict=urun_dict,
        )


        for output_file in second_run_return_file: