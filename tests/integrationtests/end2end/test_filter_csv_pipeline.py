import pandas as pd

import urgap


def test_filter_csv_pipeline(tmp_dir):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.CSV}"
                f"#unified_csvs/BSA1_xtandem_alanine_unified.csv",
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {
                    "-q": "500 < `exp_mz` < 1000",
                },
                "CompressToTar:1.0.0": {},
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    filter_node = urgap.init_unode("FilterTabularToCSV:1.0.0")
    compress_node = urgap.init_unode("CompressToTar:1.0.0")

    filter_results = filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    df = pd.read_csv(filter_results[0].path)
    assert df["sequence_start"].sum() == 9925
    assert df.shape[0] == 31

    compress_results = compress_node.run(urun_dict=urun_dict, ufiles=filter_results)
    assert compress_results[0].path.suffix == ".tar"
    untar = compress_results[0].uncompress()

    urun_dict.parameters["FilterTabularToCSV:1.0.0"].update(
        {"-q": "710 < `exp_mz` < 730"},
    )
    filter_results = filter_node.run(
        urun_dict=urun_dict,
        ufiles=untar,
    )
    df = pd.read_csv(filter_results[0].path)
    assert df["sequence_start"].sum() == 1144
    assert df.shape[0] == 4


def test_filter_csv_pipeline_latest(tmp_dir):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.CSV}"
                f"#unified_csvs/BSA1_xtandem_alanine_unified.csv",
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "FilterTabularToCSV:latest": {
                    "-q": "500 < `exp_mz` < 1000",
                },
                "CompressToTar:latest": {},
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
                "latest_exe_paths": {
                    "CompressToTar:latest": urgap.home
                    / "resources"
                    / "Compressor"
                    / "1_0_0"
                    / "compressor.py",
                    "FilterTabularToCSV:latest": urgap.home
                    / "resources"
                    / "FilterTabular"
                    / "1_0_0"
                    / "filter_tabular.py",
                },
            },
        },
    )
    filter_node = urgap.init_unode("FilterTabularToCSV:latest")
    compress_node = urgap.init_unode("CompressToTar:latest")
    filter_results = filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    df = pd.read_csv(filter_results[0].path)
    assert df["sequence_start"].sum() == 9925
    assert df.shape[0] == 31

    compress_results = compress_node.run(urun_dict=urun_dict, ufiles=filter_results)
    assert compress_results[0].path.suffix == ".tar"
    untar = compress_results[0].uncompress()

    urun_dict.parameters["FilterTabularToCSV:latest"].update(
        {"-q": "710 < `exp_mz` < 730"},
    )
    filter_results = filter_node.run(
        urun_dict=urun_dict,
        ufiles=untar,
    )
    df = pd.read_csv(filter_results[0].path)
    assert df["sequence_start"].sum() == 1144
    assert df.shape[0] == 4
