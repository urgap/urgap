import tempfile

import pytest



@pytest.mark.parametrize(
    [
        ("mongodb",),
    ],
)
def test_each_pipeline_run_creates_one_wid(
):
    (
        ufiles,
        run_dict,

    with tempfile.TemporaryDirectory() as tmpdirname:
        for x in range(4):
            urun_dict["unode_parameters"]["storage_base_uri"] = f"file://{tmpdirname}"
            print(f"--- run {x} - {urun_dict.wid}")
            test_node1.run(ufiles=ufiles, urun_dict=urun_dict)

        full_history = test_node1.utrace_history
        assert len(full_history) == 4

        counts = {"full_run": 0, "skipped_run": 0}
        for history_tuple in full_history:
            if "full_run" in history["timestamps"].keys():
                counts["full_run"] += 1
            if "skipped_run" in history["timestamps"].keys():
                counts["skipped_run"] += 1
        assert counts["full_run"] == 1
        assert counts["skipped_run"] == 3