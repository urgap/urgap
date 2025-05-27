import pprint
import tempfile

import pytest



@pytest.mark.parametrize(
    "check_if_ufilelist_can_be_tested",
    [
        (
                f"test_node_data/test.txt",
            ),
        ),
    ],
    indirect=["check_if_ufilelist_can_be_tested"],
)
def test_node_workflow_rerun_is_skipped_simple_u3(check_if_ufilelist_can_be_tested):
    ufiles = check_if_ufilelist_can_be_tested
    for unode_version in ["1.3.0", "latest"]:
        with tempfile.TemporaryDirectory() as tmpdirname:
            storage_base_uri = f"file://{tmpdirname}"
                {
                    "parameters": {
                        f"BasicFunctionTestNode:{unode_version}": {
                            "triggers_nuttin": 100,
                            "triggers_rerun": 100,
                            "triggers_rerun_-3": 100,
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                        # "remote_url": "http://localhost",
                        "storage_base_uri": storage_base_uri,
                    },
            )
            if unode_version == "latest":
                urun_dict["unode_parameters"]["latest_exe_paths"][
                    test_node1.META_INFO["unode_full_identifier"]
                ] = (
                    / "resources"
                    / "TestNodes"
                    / "BasicFunctionTestNode"
                    / "1_3_0"
                    / "basic_function.py"
                )

            print(
                """
            ------- First run -------
            )
            print("Input:")
            pprint.pprint(urun_dict)
            print("UFiles:")
            print(ufiles)
            return_file = test_node1.run(ufiles=ufiles, urun_dict=urun_dict)

            print("Output node1:")
            pprint.pprint(return_file)

            print(
                """
            ------- Second run -------

            executing second time should not trigger rerun although params are changed
            since param would not trigger rerun.
            )
            urun_dict.assign_wid()
            urun_dict["parameters"][f"BasicFunctionTestNode:{unode_version}"]["cpu"] = (
                12
            )
            # executing second time should not trigger rerun
            print("Input:")
            pprint.pprint(urun_dict)
            pprint.pprint(ufiles)

            second_run_return_file = test_node1.run(
                ufiles=ufiles,
                urun_dict=urun_dict,
            )
            print("Output:")
            pprint.pprint(second_run_return_file)