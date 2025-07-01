import pandas as pd
import pytest

import urgap


@pytest.mark.parametrize(
    "provide_uctl_server",
    [("FilterTabularToCSV:latest", "CompressToTar:latest")],
    indirect=["provide_uctl_server"],
)
def test_filter_csv_pipeline(tmp_dir, provide_uctl_server):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.CSV}"
                f"#unified_csvs/BSA1_xtandem_alanine_unified.csv",
            ),
        ],
    )
    urun_dict_filter = urgap.URunDict(
        {
            "parameters": {
                "FilterTabularToCSV:latest": {
                    "-q": "500 < `exp_mz` < 1000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
                "remote_url": "http://localhost",
                "latest_exe_paths": {
                    "FilterTabularToCSV:latest": urgap.home
                    / "resources"
                    / "FilterTabular"
                    / "1_0_0"
                    / "filter_tabular.py",
                },
            },
        },
    )
    urun_dict_compress = urgap.URunDict(
        {
            "parameters": {"CompressToTar:latest": {}},
            "unode_parameters": {
                "remote_url": "http://localhost",
                "storage_base_uri": f"file://{tmp_dir}",
                "latest_exe_paths": {
                    "CompressToTar:latest": urgap.home
                    / "resources"
                    / "Compressor"
                    / "1_0_0"
                    / "compressor.py",
                },
            },
            "wid": urun_dict_filter["wid"],
        },
    )
    filter_tab_to_csv_node = urgap.init_unode("FilterTabularToCSV:latest")
    compress_to_tar_node = urgap.init_unode("CompressToTar:latest")

    filter_1 = filter_tab_to_csv_node.run(urun_dict=urun_dict_filter, ufiles=ufiles)
    df = pd.read_csv(filter_1[0].path)
    assert df["sequence_start"].sum() == 9925
    assert df.shape[0] == 31

    tar_1 = compress_to_tar_node.run(urun_dict=urun_dict_compress, ufiles=filter_1)
    assert tar_1[0].path.suffix == ".tar"
    untar_1 = tar_1[0].uncompress()

    urun_dict_filter.parameters["FilterTabularToCSV:latest"].update(
        {"-q": "710 < `exp_mz` < 730"},
    )
    filtered_1a = filter_tab_to_csv_node.run(urun_dict=urun_dict_filter, ufiles=untar_1)
    df = pd.read_csv(filtered_1a[0].path)
    assert df["sequence_start"].sum() == 1144
    assert df.shape[0] == 4