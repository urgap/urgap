import pandas as pd

import urgap


@pytest.mark.parametrize(
    [
    ],
)
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
            ),
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                unode: {
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmpdir}",
                "latest_exe_paths": {
                    "FilterTabularToParquet:latest": urgap.home
                    / "resources"
                    / "FilterTabular"
                    / "2_0_0"
                    / "filter_tabular.py",
                },
            },
        },
    )
    parquet_filter_node = urgap.init_unode(unode)
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToParquet:1.0.0",
        "FilterTabularToParquet:2.0.0",
    ],
)
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.PARQUET}"
                f"#parquets/demo.parquet",
            ),
    )
    urun_dict = urgap.URunDict(
        {
            "unode_parameters": {
                "storage_base_uri": f"file://{tmpdir}",
            },
        },
    )
    parquet_filter_node = urgap.init_unode(unode)
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToParquet:1.0.0",
        "FilterTabularToParquet:2.0.0",
    ],
)
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.PARQUET}"
                f"#parquets/demo.parquet",
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {unode: {"-q": None}},
            "unode_parameters": {
            },
        },
    )
    parquet_filter_node = urgap.init_unode(unode)
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToParquet:1.0.0",
        "FilterTabularToParquet:2.0.0",
    ],
)
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "unode_parameters": {
            },
        },
    )
    parquet_filter_node = urgap.init_unode(unode)
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToParquet:1.0.0",
        "FilterTabularToParquet:2.0.0",
    ],
)
def test_wrapper_filter_tabular_csv_and_parquet_input(tmp_dir, unode):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.PARQUET}"
                f"#parquets/demo_from_csv.parquet",
            ),
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.CSV}"
                f"#unified_csvs/demo.csv",
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                unode: {
                    "-q": "`spectrum_id` > 3000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    parquet_filter_node = urgap.init_unode(unode)
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)
    assert df.shape[0] == 8
    assert df["Sequence Start"].sum() == 2142