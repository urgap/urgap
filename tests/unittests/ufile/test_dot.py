

def test_ufile_dot(tmp_dir):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.TABULAR}"
                f"#unified_csvs/demo.csv",
            ),
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.XLSX}"
                f"#xlsx/demo.xlsx",
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {
                    "-q": "`spectrum_id` > 3000",
                },
                    "-q": "`spectrum_id` > 4000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    filter_node = urgap.init_unode("FilterTabularToCSV:1.0.0")
    filtered_csv = filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_csv[0].path.exists()
