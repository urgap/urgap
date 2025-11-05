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
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                    },
                },
            ),
            ["TestNode1:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_node_workflow_rerun_is_skipped_changed_not_triggering_rerun(
    provide_clean_test_node_dirs,
):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    storage_base_uri = ufiles[0].storage_base_uri
    test_node1 = test_nodes["TestNode1:1.0.0"]

    # executing first time
    print(
        """
    ------- First run -------
    """,
    )
    print("Input:")
    print("------")
    pprint.pprint(urun_dict)
    print(ufiles)
    return_file = test_node1.run(ufiles=ufiles, urun_dict=urun_dict)
    print("Output node:")
    print("------------")
    pprint.pprint(return_file)

    pac_id, wid = test_node1.utrace_history[-1]
    report = urgap.UReport(wid=wid)
    assert report.get_trace(pac_id, wid, storage_base_uri).was_run is True

    print(
        """
    ------- Second run -------
    """,
    )
    urun_dict.assign_wid()
    test_node1.run(
        ufiles=ufiles,
        urun_dict=urun_dict,
    )
    pac_id, wid = test_node1.utrace_history[-1]
    report = urgap.UReport(wid=wid)
    assert report.get_trace(pac_id, wid, storage_base_uri).was_skipped is True