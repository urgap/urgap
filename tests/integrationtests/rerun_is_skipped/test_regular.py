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
def test_node_workflow_rerun_is_skipped_simple(provide_clean_test_node_dirs):
    print("Input:")
    print("Output node1:")
    pprint.pprint(return_file)
    print("Input:")

    print("Output:")
    pprint.pprint(second_run_return_file)