import pprint
import tempfile

import pytest



@pytest.mark.parametrize(
    "check_if_ufilelist_can_be_tested",
    [
            [
            ],
    ],
    indirect=["check_if_ufilelist_can_be_tested"],
)
def test_node_workflow_rerun_is_skipped_changed_not_triggering_rerun(
    check_if_ufilelist_can_be_tested,
):
    ufiles = check_if_ufilelist_can_be_tested
    with tempfile.TemporaryDirectory() as tmpdirname:
        storage_base_uri = f"file://{tmpdirname}"
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
        )
        print("Output node3 - first run:")
        pprint.pprint(return_file_node3_first_run)
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
