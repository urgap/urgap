import tempfile

import pytest

import urgap


@pytest.mark.parametrize(
    "provide_standard_TestNode1_setup_and_set_umeta_interface",
    [
        ("mongodb",),
    ],
    indirect=["provide_standard_TestNode1_setup_and_set_umeta_interface"],
)
def test_each_pipeline_run_creates_one_wid(
    provide_standard_TestNode1_setup_and_set_umeta_interface,
):
    (
        ufiles,
        run_dict,
    ) = provide_standard_TestNode1_setup_and_set_umeta_interface

    with tempfile.TemporaryDirectory() as tmpdirname:
        test_node1 = urgap.init_node("TestNode1:1.0.0")
        for x in range(4):
            urun_dict = urgap.urun_dict.URunDict(run_dict)
            urun_dict["unode_parameters"]["storage_base_uri"] = f"file://{tmpdirname}"
            print(f"--- run {x} - {urun_dict.wid}")
            test_node1.run(ufiles=ufiles, urun_dict=urun_dict)

        full_history = test_node1.utrace_history
        assert len(full_history) == 4

        counts = {"full_run": 0, "skipped_run": 0}
        for history_tuple in full_history:
            pac_id, wid = history_tuple
            report = urgap.UReport(wid=wid)
            history = report.get_trace(pac_id, wid).get_history()
            if "full_run" in history["timestamps"].keys():
                counts["full_run"] += 1
            if "skipped_run" in history["timestamps"].keys():
                counts["skipped_run"] += 1
        assert counts["full_run"] == 1
        assert counts["skipped_run"] == 3