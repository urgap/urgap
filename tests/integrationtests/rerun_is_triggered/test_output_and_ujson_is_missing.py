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
                },
                "unode_parameters": {
                    "record_skipped_runs": True,
                },
        )
        print("Input:")
        pprint.pprint(urun_dict)
        print(ufiles)
        return_file = test_node1.run(ufiles=ufiles, urun_dict=urun_dict)
        print("Output node:")
        pprint.pprint(return_file)

        for output_file in return_file:
            test_node1.remove_output_folder(output_file)
            assert output_file.remote_object_exists() is False

