import pprint
import tempfile

import pytest



@pytest.mark.parametrize(
    "check_if_ufilelist_can_be_tested",
    [
            [
                ),
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
                    "BasicFunctionTestNode:1.1.0": {
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

        print(
            """
            executing second time should be trigger rerun since re-run param has changed
        """,
        )
        urun_dict["parameters"]["BasicFunctionTestNode:1.1.0"]["triggers_rerun"] = 200
        print(
            """
        ------- Second run -------
        """,
        )
        urun_dict.assign_wid()

        print("Input:", urun_dict)
        test_node1.run(
            ufiles=ufiles,
            urun_dict=urun_dict,
        )