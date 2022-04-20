import pprint

import pytest



@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            ),
                {
                    "parameters": {
                    },
                    },
            ),
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_node_workflow_rerun_is_skipped_simple(provide_clean_test_node_dirs):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    print("Input:")
    pprint.pprint(urun_dict)
    print("UFiles:")
    print(ufiles)
    return_file = test_node1.run(ufiles=ufiles, urun_dict=urun_dict)
    print("Output node1:")
    pprint.pprint(return_file)
    print("Input:")
    pprint.pprint(urun_dict)
    pprint.pprint(ufiles)

    print("Output:")
    pprint.pprint(second_run_return_file)