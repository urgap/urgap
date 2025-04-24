import pprint
import tempfile

import pytest



@pytest.mark.parametrize(
    "check_if_ufilelist_can_be_tested",
    [
            [
    ],
    indirect=["check_if_ufilelist_can_be_tested"],
)
def test_node_workflow_rerun_is_skipped_simple(check_if_ufilelist_can_be_tested):
    ufiles = check_if_ufilelist_can_be_tested
    with tempfile.TemporaryDirectory() as tmpdirname:
            {
                "parameters": {
                    "TestNode1:1.0.0": {
                        "triggers_nuttin": 100,
                        "triggers_rerun": 100,
                        "triggers_rerun_-3": 100,
                },
                "unode_parameters": {
                    "record_skipped_runs": True,
                },
        )

        print(
            """
        ------- First run -------
        )
        print("Input:")
        print("------")
        pprint.pprint(urun_dict)
        print(ufiles)
        return_file = test_node1.run(ufiles=ufiles, urun_dict=urun_dict)
        print("Output node:")
        print("------------")
        pprint.pprint(return_file)

        print(
            """
            Removing output file but not json - should trigger second run!
        )
        for output_file in return_file:
            test_node1.remove_output_folder(output_file)

        print(
            """
        ------- Second run -------
        )
        urun_dict.assign_wid()

        test_node1.run(
            ufiles=ufiles,
            urun_dict=urun_dict,
        )
