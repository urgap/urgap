import pytest

import urgap


@pytest.mark.parametrize(
    "provide_clean_node_dirs",
    [
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.proteomics.validator.PEPTIDEFOREST_CSV}"
                f"#unified_csvs/demo.csv",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "FilterTabularToCSV:1.0.0": {
                            "-q": "`spectrum_id` > 3000",
                        },
                    },
                    "unode_parameters": {
                        "force": True,
                    },
                },
            ),
            ["FilterTabularToCSV:1.0.0"],
        ),
    ],
    indirect=["provide_clean_node_dirs"],
)
def test_lineage_root(provide_clean_node_dirs, tmp_dir):
    nodes, ufiles, urun_dict = provide_clean_node_dirs
    urun_dict["unode_parameters"].update({"storage_base_uri": f"file://{tmp_dir}"})
    csv_filter_node = nodes["FilterTabularToCSV:1.0.0"]
    filtered_csv = csv_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_csv[0].path.exists()
    assert filtered_csv[0].identify_lineage_root_files()[0] == ufiles[0].ucfs