import pandas as pd

import urgap


@pytest.mark.parametrize(
    "unode,query",
    [
        ("FilterTabularToParquet:1.0.0", "3100 > spectrum_id > 3000"),
        ("FilterTabularToParquet:2.0.0", "3100 > spectrum_id AND spectrum_id > 3000"),
        ("FilterTabularToParquet:latest", "3100 > spectrum_id AND spectrum_id > 3000"),
    ],
)
def test_wrapper_filter_tabular_csv_input(tmpdir, unode, query):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.proteomics.validator.PEPTIDEFOREST_CSV}"
                f"#unified_csvs/demo.csv",
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                unode: {
                    "-q": query,
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
    assert df.shape[0] == 1
    assert df["Sequence Start"].sum() == 588


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToParquet:1.0.0",
        "FilterTabularToParquet:2.0.0",
    ],
)
def test_wrapper_filter_tabular_parquet(tmpdir, unode):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.PARQUET}"
                f"#parquets/demo.parquet",
            ),
        ]
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                unode: {
                    "-q": "`include_this` == 'yes'",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmpdir}",
            },
        },
    )
    parquet_filter_node = urgap.init_unode(unode)
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)
    assert df.shape[0] == 2


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToParquet:1.0.0",
        "FilterTabularToParquet:2.0.0",
    ],
)
def test_wrapper_filter_tabular_parquet_without_query(tmpdir, unode):
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
                "storage_base_uri": f"file://{tmpdir}",
            },
        },
    )
    parquet_filter_node = urgap.init_unode(unode)
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)
    assert df.shape[0] == 3


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToParquet:1.0.0",
        "FilterTabularToParquet:2.0.0",
    ],
)
def test_wrapper_filter_tabular_parquet_2_without_query(tmp_dir, unode):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.PARQUET}"
                f"#parquets/demo.parquet",
            ),
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.PARQUET}"
                f"#parquets/demo2.parquet",
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {unode: {"-q": None}},
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    parquet_filter_node = urgap.init_unode(unode)
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)
    assert df.shape[0] == 6


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