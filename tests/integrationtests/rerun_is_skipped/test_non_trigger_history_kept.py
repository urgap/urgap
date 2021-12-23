import pprint
import pytest



@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_node_workflow_rerun_is_skipped_changed_not_triggering_rerun(
    provide_clean_test_node_dirs,
):

    print("Input:")
    print(ufiles)
    print("Output node:")
    pprint.pprint(return_file)
