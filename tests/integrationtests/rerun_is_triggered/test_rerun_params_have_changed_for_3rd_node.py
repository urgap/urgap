import pprint
import tempfile

import pytest

import urgap


@pytest.mark.parametrize(
    "check_if_ufilelist_can_be_tested",
    [
        urgap.UFileList(
            [
                urgap.UFile(
                    uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                    f"test_node_data/test.txt",
                ),
            ],
        ),
        urgap.UFileList(
            [
                urgap.UFile(
                    uri=f"gcs-libcloud://urgap_test?uftype={urgap.uftypes.test.TEST_FILE1}#"
                    f"test_node_data/test.txt",
                ),
            ],
        ),
        urgap.UFileList(
            [
                urgap.UFile(
                    uri=f"local-libcloud://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                    f"test_node_data/test.txt",
                ),
            ],
        ),
        urgap.UFileList(
            [
                urgap.UFile(
                    uri=f"minio-libcloud://localhost:9000/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                    f"test_node_data/test.txt",
                ),
            ],
        ),
    ],
    indirect=["check_if_ufilelist_can_be_tested"],
)
def test_node_workflow_rerun_is_skipped_changed_not_triggering_rerun(
    check_if_ufilelist_can_be_tested,
):
    ufiles = check_if_ufilelist_can_be_tested
    with tempfile.TemporaryDirectory() as tmpdirname:
        storage_base_uri = f"file://{tmpdirname}"
        urun_dict = urgap.URunDict(
            {
                "parameters": {
                    "TestNode1:1.0.0": {
                        "triggers_nuttin": 100,
                        "triggers_rerun": 100,
                        "no_rerun_node_trigger": 100,
                    },
                    "BasicFunctionTestNode:1.3.0": {
                        "triggers_nuttin": 100,
                        "triggers_rerun": 100,
                        "no_rerun_node_trigger": 100,
                    },
                },
                "unode_parameters": {
                    "record_skipped_runs": True,
                    "storage_base_uri": storage_base_uri,
                },
            },
        )
        rerun_test_node = urgap.init_node("TestNode1:1.0.0")
        basic_test_node = urgap.init_node("BasicFunctionTestNode:1.3.0")

        # executing first time
        print(
            """
        ------- First run -------
        """,
        )
        print("Input:")
        pprint.pprint(urun_dict)
        return_file = rerun_test_node.run(ufiles=ufiles, urun_dict=urun_dict)
        print("Output node1:")
        pprint.pprint(return_file)

        return_file_node3_first_run = basic_test_node.run(
            ufiles=ufiles,
            urun_dict=urun_dict,
        )
        print("Output node3 - first run:")
        pprint.pprint(return_file_node3_first_run)
        # report3_1 = urgap.UReport(ufile=return_file_node3_first_run[0])
        print(
            """

            executing second time should be trigger on Node 3 since re-run param has changed

        """,
        )

        urun_dict["parameters"]["BasicFunctionTestNode:1.3.0"][
            "no_rerun_node_trigger"
        ] = None
        urun_dict["parameters"]["TestNode1:1.0.0"]["no_rerun_node_trigger"] = None
        print(
            """
        ------- Second run -------
        """,
        )
        urun_dict.assign_wid()
        print("Input:", urun_dict)
        return_file_node1_second_run = rerun_test_node.run(
            ufiles=ufiles,
            urun_dict=urun_dict,
        )
        return_file_node3_second_run = basic_test_node.run(
            ufiles=ufiles,
            urun_dict=urun_dict,
        )
        pac_id, wid = rerun_test_node.utrace_history[-1]
        report = urgap.UReport(wid=wid)
        assert report.get_trace(pac_id, wid, storage_base_uri).was_skipped is True

        pac_id, wid = basic_test_node.utrace_history[-1]
        report = urgap.UReport(wid=wid)
        assert report.get_trace(pac_id, wid, storage_base_uri).was_skipped is False
