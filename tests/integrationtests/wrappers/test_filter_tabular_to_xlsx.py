import pandas as pd
import pytest

import urgap


@pytest.mark.parametrize(
    [
    ],
)
    ufiles = urgap.UFileList(
        [
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
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
                "latest_exe_paths": {
                    "FilterTabularToXlsx:latest": urgap.home
                    / "resources"
                    / "FilterTabular"
                    / "2_0_0"
                    / "filter_tabular.py",
                },
            },
        },
    )
    FilterTabularToXlsx_node = urgap.init_unode(unode)
    filtered_xlsx = FilterTabularToXlsx_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_xlsx[0].path.exists()
    df = pd.read_excel(filtered_xlsx[0].path)


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToXlsx:1.0.0",
        "FilterTabularToXlsx:2.0.0",
    ],
)
def test_wrapper_filter_xlsx_csv_input(tmp_dir, unode):
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
                    "-q": "`spectrum_id` > 3000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    FilterTabularToXlsx_node = urgap.init_unode(unode)
    filtered_xlsx = FilterTabularToXlsx_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_xlsx[0].path.exists()
    df = pd.read_excel(filtered_xlsx[0].path)
    assert df.shape[0] == 4
    assert df["Sequence Start"].sum() == 1071


@pytest.mark.parametrize(
    "unode",
    [
        "FilterTabularToXlsx:1.0.0",
        "FilterTabularToXlsx:2.0.0",
    ],
)
def test_wrapper_filter_xlsx_2_input(tmp_dir, unode):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.proteomics.validator.PEPTIDEFOREST_CSV}"
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
                    "-q": "`spectrum_id` > 3000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    FilterTabularToXlsx_node = urgap.init_unode(unode)
    filtered_xlsx = FilterTabularToXlsx_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_xlsx[0].path.exists()
    df = pd.read_excel(filtered_xlsx[0].path)
    assert df.shape[0] == 8
    assert df["Sequence Start"].sum() == 2142