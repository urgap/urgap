import urgap


def test_trailing_separator_in_storage_base_uri_normalization(tmp_dir):
    filter_csv_node = urgap.init_node("FilterTabularToCSV:1.0.0")

    f1 = urgap.UFile(
        uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.CSV}#unified_csvs/BSA1_xtandem_alanine_unified.csv",
    )
    f2 = urgap.UFile(
        uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.CSV}#unified_csvs/demo.csv",
    )
    urun_dict = urgap.urun_dict.URunDict(
        {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {
                    "-q": "spectrum_title != 'DiesDasAnanas'",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )

    # should not raise TypeError (see unode.py line 131)
    filter_csv_node.run(ufiles=[f1, f2], urun_dict=urun_dict)
