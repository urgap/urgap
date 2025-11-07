import tempfile

import pytest

import urgap


@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE2}#"
                f"test_node_data/test.txt",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "TestNode5:1.0.0": {
                            urgap.uftypes.test.TEST_FILE1: 1,
                            urgap.uftypes.test.TEST_FILE2: 1,
                            urgap.uftypes.test.MITSURUGI: 3,
                        },
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                    },
                },
            ),
            ["TestNode5:1.0.0"],
        ),
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE2}#"
                f"test_node_data/test.txt",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "TestNode5:1.0.0": {
                            urgap.uftypes.test.TEST_FILE1: 0,
                            urgap.uftypes.test.TEST_FILE2: 9,
                            urgap.uftypes.test.MITSURUGI: 3,
                        },
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                    },
                },
            ),
            ["TestNode5:1.0.0"],
        ),
        (
            [
                urgap.UFile(
                    uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE2}#"
                    f"test_node_data/test.txt",
                ),
                urgap.UFile(
                    uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                    f"test_node_data/test.txt",
                ),
            ],
            urgap.URunDict(
                {
                    "parameters": {
                        "TestNode5:1.0.0": {
                            urgap.uftypes.test.TEST_FILE1: 0,
                            urgap.uftypes.test.TEST_FILE2: 1,
                            urgap.uftypes.test.MITSURUGI: 3,
                        },
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                    },
                },
            ),
            ["TestNode5:1.0.0"],
        ),
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE2}#"
                f"test_node_data/test.txt",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "TestNode5:1.0.0": {
                            urgap.uftypes.test.TEST_FILE1: 0,
                            urgap.uftypes.test.TEST_FILE2: 1,
                            urgap.uftypes.test.MITSURUGI: 3,
                        },
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                    },
                },
            ),
            ["TestNode5:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_node_workflow_rerun_is_skipped_simple(provide_clean_test_node_dirs):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    with tempfile.TemporaryDirectory() as tmpdirname:
        storage_base_uri = f"file://{tmpdirname}"
        urun_dict["unode_parameters"]["storage_base_uri"] = storage_base_uri
        test_node9 = test_nodes["TestNode5:1.0.0"]
        return_file = test_node9.run(ufiles=ufiles, urun_dict=urun_dict)

        for uftype, n in urun_dict.parameters["TestNode5:1.0.0"].items():
            assert n == return_file.number_of_uftypes().get(uftype, 0)

        pac_id, wid = test_node9.utrace_history[-1]
        report = urgap.UReport(wid=wid)
        assert report.get_trace(pac_id, wid, storage_base_uri).was_run is True

        second_run_return_file = test_node9.run(
            ufiles=ufiles,
            urun_dict=urun_dict,
        )
        for uftype, n in urun_dict.parameters["TestNode5:1.0.0"].items():
            assert n == second_run_return_file.number_of_uftypes().get(uftype, 0)

        pac_id, wid = test_node9.utrace_history[-1]
        report = urgap.UReport(wid=wid)
        assert report.get_trace(pac_id, wid, storage_base_uri).was_skipped is True

        # ut2 = urgap.UTrace(wid=wid, pac_id=pac_id)
        # assert report2.was_skipped(wid, pac_id) is True

        for output_file in second_run_return_file:
            test_node9.remove_output_folder(output_file=output_file)
