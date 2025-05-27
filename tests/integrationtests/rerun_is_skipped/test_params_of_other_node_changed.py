import pprint

import pytest



@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            ),
                {
                    "parameters": {
                        "TestNode1:1.0.0": {
                            "triggers_nuttin": 100,
                            "triggers_rerun": 100,
                            "triggers_rerun_-3": 100,
                        },
                        "TestNode3:1.0.0": {
                            "triggers_nuttin": 100,
                            "triggers_rerun": 100,
                            "triggers_rerun_-3": 100,
                        },
                    },
                    },
            ),
            ["TestNode1:1.0.0", "TestNode3:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_node_workflow_rerun_is_skipped_if_parameter_of_other_node_change(
    provide_clean_test_node_dirs,
):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    storage_base_uri = ufiles[0].storage_base_uri
    test_node1 = test_nodes["TestNode1:1.0.0"]
    test_node3 = test_nodes["TestNode3:1.0.0"]
    print("Input:")
    pprint.pprint(urun_dict)
    print("UFiles:")
    print(ufiles)
    return_file = test_node1.run(ufiles=ufiles, urun_dict=urun_dict)
    print("Output node1:")
    pprint.pprint(return_file)

    return_file_node3_first_run = test_node3.run(ufiles=ufiles, urun_dict=urun_dict)
    with open(return_file_node3_first_run[0].path) as f:
        assert f.readline().strip() == "TestNode3"
    print("Output node3 - first run:")
    pprint.pprint(return_file_node3_first_run)


    urun_dict["parameters"]["triggers_nuttin"] = 200
    urun_dict.assign_wid()

    pprint.pprint(return_file_node3_second_run)
