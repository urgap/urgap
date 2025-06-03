

def test_trailing_separator_in_storage_base_uri_normalization(tmp_dir):

    )
    )
        {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {
                    "-q": "spectrum_title != 'DiesDasAnanas'",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )

    # should not raise TypeError (see unode.py line 131)
    filter_csv_node.run(ufiles=[f1, f2], urun_dict=urun_dict)