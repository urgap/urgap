import pandas as pd



@pytest.mark.parametrize(
    "provide_uctl_server",
    [("FilterTabularToCSV:latest", "CompressToTar:latest")],
    indirect=["provide_uctl_server"],
)
def test_filter_csv_pipeline(tmp_dir, provide_uctl_server):
        [
    )
        {
            "parameters": {
                "FilterTabularToCSV:latest": {
                    "-q": "500 < `exp_mz` < 1000",
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
                "remote_url": "http://localhost",
                "latest_exe_paths": {
                    / "resources"
                    / "FilterTabular"
                    / "1_0_0"
                },
            },
    )
        {
            "parameters": {"CompressToTar:latest": {}},
            "unode_parameters": {
                "remote_url": "http://localhost",
                "storage_base_uri": f"file://{tmp_dir}",
                "latest_exe_paths": {
                    / "resources"
                    / "Compressor"
                    / "1_0_0"
                },
            },
            "wid": urun_dict_filter["wid"],
    )

    filter_1 = filter_tab_to_csv_node.run(urun_dict=urun_dict_filter, ufiles=ufiles)
    df = pd.read_csv(filter_1[0].path)
    assert df["sequence_start"].sum() == 9925
    assert df.shape[0] == 31

    tar_1 = compress_to_tar_node.run(urun_dict=urun_dict_compress, ufiles=filter_1)
    assert tar_1[0].path.suffix == ".tar"
    untar_1 = tar_1[0].uncompress()

    urun_dict_filter.parameters["FilterTabularToCSV:latest"].update(
    )
    filtered_1a = filter_tab_to_csv_node.run(urun_dict=urun_dict_filter, ufiles=untar_1)
    df = pd.read_csv(filtered_1a[0].path)
    assert df["sequence_start"].sum() == 1144
    assert df.shape[0] == 4