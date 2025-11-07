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
        (
            urgap.UFile(
                uri=f"gcs-libcloud://urgap_test?uftype={urgap.uftypes.test.TEST_FILE1}#"
                "test_node_data/test.txt",
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
        (
            urgap.UFile(
                uri=f"local-libcloud://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
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
        (
            urgap.UFile(
                uri=f"minio-libcloud://localhost:9000/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                "test_node_data/test.txt",
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
    pprint.pprint(urun_dict)
    return_file = test_node1.run(ufiles=ufiles, urun_dict=urun_dict)
    print("Output node1:")
    pprint.pprint(return_file)

    pac_id, wid = test_node1.utrace_history[-1]
    report = urgap.UReport(wid=wid)
    assert report.get_trace(pac_id, wid, storage_base_uri).was_run is True

    print(
        """
    ------- Changing param that triggers no rerun -------
    """,
    )
    urun_dict["parameters"]["TestNode1:1.0.0"]["triggers_nuttin"] = 200
    print(
        """
    ------- Second run -------
    """,
    )
    urun_dict.assign_wid()
    print("Input:")
    pprint.pprint(urun_dict)
    # executing second time should not trigger rerun although params are changed
    # sice param would not trigger rerun

    second_run_return_file = test_node1.run(
        ufiles=ufiles,
        urun_dict=urun_dict,
    )
    print("Output:")
    pprint.pprint(second_run_return_file)
    pac_id, wid = test_node1.utrace_history[-1]
    report = urgap.UReport(wid=wid)
    assert report.get_trace(pac_id, wid, storage_base_uri).was_skipped is True
