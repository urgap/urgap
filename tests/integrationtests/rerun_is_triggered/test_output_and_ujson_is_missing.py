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
        )
    ],
    indirect=["check_if_ufilelist_can_be_tested"],
)
def test_node_workflow_rerun_is_skipped_simple(check_if_ufilelist_can_be_tested):
    ufiles = check_if_ufilelist_can_be_tested
    with tempfile.TemporaryDirectory() as tmpdirname:
        storage_base_uri = f"file://{tmpdirname}"
        urun_dict = urgap.URunDict(
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
                    "storage_base_uri": storage_base_uri,
                },
            },
        )
        test_node1 = urgap.init_node("TestNode1:1.0.0")

        print("\n------- First run -------\n")
        print("Input:")
        pprint.pprint(urun_dict)
        print(ufiles)
        return_file = test_node1.run(ufiles=ufiles, urun_dict=urun_dict)
        print("Output node:")
        pprint.pprint(return_file)

        for output_file in return_file:
            test_node1.remove_output_folder(output_file)
            assert output_file.remote_object_exists() is False

        print("\n------- Second run -------\n")
        urun_dict.assign_wid()
        test_node1.run(ufiles=ufiles, urun_dict=urun_dict)

        pac_id, wid = test_node1.utrace_history[-1]
        report = urgap.UReport(wid=wid)
        assert report.get_trace(pac_id, wid, storage_base_uri).was_run is True