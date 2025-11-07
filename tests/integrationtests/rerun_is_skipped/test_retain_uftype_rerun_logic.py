import pytest

import urgap


@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.proteomics.converter.PYIOHAT_CSV}#"
                f"unified_csvs/BSA1_xtandem_alanine_unified.csv",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "FilterTabularToCSV:1.0.0": {
                            "-q": "569.750 < `exp_mz` < 569.760",
                        },
                    },
                    "unode_parameters": {
                        "record_skipped_runs": True,
                    },
                },
            ),
            ["FilterTabularToCSV:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_node_workflow_rerun_is_skipped_simple(provide_clean_test_node_dirs, tmp_dir):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    retain_uftype = True
    storage_base_uri = f"file://{tmp_dir}"
    urun_dict["unode_parameters"]["storage_base_uri"] = storage_base_uri
    filter_csv = test_nodes["FilterTabularToCSV:1.0.0"]
    return_file = filter_csv.run(
        ufiles=ufiles,
        urun_dict=urun_dict,
        retain_uftype=retain_uftype,
    )
    pac_id, wid = filter_csv.utrace_history[-1]
    report = urgap.UReport(wid=wid)
    assert report.get_trace(pac_id, wid, storage_base_uri).was_run is True

    urun_dict.reassign_wid()

    second_run_return_file = filter_csv.run(
        ufiles=ufiles,
        urun_dict=urun_dict,
        retain_uftype=retain_uftype,
    )

    pac_id, wid = filter_csv.utrace_history[-1]
    report = urgap.UReport(wid=wid)
    assert report.get_trace(pac_id, wid, storage_base_uri).was_skipped is True

    assert len(second_run_return_file) == len(return_file)
