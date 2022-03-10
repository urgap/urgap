import pprint

import pytest



@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_node_workflow_rerun_is_skipped_if_parameter_of_other_node_change(
    provide_clean_test_node_dirs,
):
    print("Input:")
    print("UFiles:")
    print(ufiles)
    print("Output node1:")
    pprint.pprint(return_file)

    print("Output node3 - first run:")
    pprint.pprint(return_file_node3_first_run)

    pprint.pprint(return_file_node3_second_run)
