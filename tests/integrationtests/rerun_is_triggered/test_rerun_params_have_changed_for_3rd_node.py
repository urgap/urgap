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
def test_node_workflow_rerun_is_skipped_changed_not_triggering_rerun(
    check_if_ufilelist_can_be_tested,
):
    ufiles = check_if_ufilelist_can_be_tested
    with tempfile.TemporaryDirectory() as tmpdirname:
            {
                "parameters": {
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
        pprint.pprint(urun_dict)
        print("Output node1:")
        pprint.pprint(return_file)

        print("Output node3 - first run:")
        pprint.pprint(return_file_node3_first_run)
        print(
            """

            executing second time should be trigger on Node 3 since re-run param has changed

        )

        print(
            """
        ------- Second run -------
        )
        urun_dict.assign_wid()
        print("Input:", urun_dict)
            ufiles=ufiles,
            urun_dict=urun_dict,
        )
            ufiles=ufiles,
            urun_dict=urun_dict,
        )
