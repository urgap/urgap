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
        (
            [
                ),
                ),
            ],
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
        return_file = test_node9.run(ufiles=ufiles, urun_dict=urun_dict)

            assert n == return_file.number_of_uftypes().get(uftype, 0)

        second_run_return_file = test_node9.run(
            ufiles=ufiles,
            urun_dict=urun_dict,
        )
            assert n == second_run_return_file.number_of_uftypes().get(uftype, 0)



        for output_file in second_run_return_file:
            test_node9.remove_output_folder(output_file=output_file)