import pprint

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
                    "unode_parameters": {
                        "record_skipped_runs": True,
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
    # executing first time
    print(
        """
    ------- First run -------
    """,
    )
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

    pac_id, wid = test_node1.utrace_history[-1]
    report = urgap.UReport(wid=wid)
    assert report.get_trace(pac_id, wid, storage_base_uri).was_run is True
    pac_id, wid = test_node3.utrace_history[-1]
    report = urgap.UReport(wid=wid)
    assert report.get_trace(pac_id, wid, storage_base_uri).was_run is True

    print(
        """
    --- executing second time should not trigger rerun of node3 as parameter does not map
    thus not rerun is triggered ---
    """,
    )
    urun_dict["parameters"]["triggers_nuttin"] = 200
    # urun_dict["parameters"]["triggers_rerun"] = 200
    print(
        """
    ------- Second run -------
    """,
    )
    urun_dict.assign_wid()

    print("Input:", urun_dict)
    return_file_node3_second_run = test_node3.run(
        ufiles=ufiles,
        urun_dict=urun_dict,
    )
    print("Output node3 - Second run:")
    pprint.pprint(return_file_node3_second_run)

    pac_id, wid = test_node3.utrace_history[-1]
    report = urgap.UReport(wid=wid)
    assert report.get_trace(pac_id, wid, storage_base_uri).was_skipped is True