import pandas as pd
import pytest

import urgap


@pytest.mark.parametrize(
    "unode,query",
    [
        ("FilterTabularToCSV:1.0.0", "3100 > spectrum_id > 3000"),
        ("FilterTabularToCSV:2.0.0", "3100 > spectrum_id AND spectrum_id > 3000"),
        ("FilterTabularToCSV:latest", "3100 > spectrum_id AND spectrum_id > 3000"),
    ],
)
def test_wrapper_filter_csv(tmp_dir, unode, query):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.genomics.plink.BIM}"
                f"#unified_csvs/demo.csv",
            ),
        ]
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                unode: {
                    "-q": query,
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
                "latest_exe_paths": {
                    "FilterTabularToCSV:latest": urgap.home
                    / "resources"
                    / "FilterTabular"
                    / "2_0_0"
                    / "filter_tabular.py",
                },
            },
        },
    )
    csv_filter_node = urgap.init_unode(unode)
    filtered_csv = csv_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_csv[0].path.exists()
    df = pd.read_csv(filtered_csv[0].path)
    assert df.shape[0] == 1
    assert df["Sequence Start"].sum() == 588


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToCSV:1.0.0",
        "FilterTabularToCSV:2.0.0",
    ],
)
def test_wrapper_filter_csv_parquet_input(tmp_dir, unode):
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
            "parameters": {
                unode: {
                    "-q": "include_this == 'yes'",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    csv_filter_node = urgap.init_unode(unode)
    filtered_csv = csv_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_csv[0].path.exists()
    assert filtered_csv[0].uftype == ".any.csv"
    df = pd.read_csv(filtered_csv[0].path)
    assert df.shape[0] == 2


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToCSV:1.0.0",
        "FilterTabularToCSV:2.0.0",
    ],
)
def test_wrapper_filter_csv_parquet_input_without_query(tmp_dir, unode):
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
            "parameters": {
                unode: {
                    "-q": None,
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    csv_filter_node = urgap.init_unode(unode)
    filtered_csv = csv_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_csv[0].path.exists()
    assert filtered_csv[0].uftype == ".any.csv"
    df = pd.read_csv(filtered_csv[0].path)
    assert df.shape[0] == 3


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToCSV:1.0.0",
        "FilterTabularToCSV:2.0.0",
    ],
)
def test_wrapper_filter_csv_and_xlsx(tmp_dir, unode):
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
                unode: {
                    "-q": "spectrum_id > 3000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    csv_filter_node = urgap.init_unode(unode)
    filtered_csv = csv_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_csv[0].path.exists()
    df = pd.read_csv(filtered_csv[0].path)
    assert df.shape[0] == 8
    assert df["Sequence Start"].sum() == 2142
