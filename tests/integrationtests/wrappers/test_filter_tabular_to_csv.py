import pandas as pd
import pytest

import urgap


@pytest.mark.parametrize(
    [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.proteomics.validator.PEPTIDEFOREST_CSV}"
                f"#unified_csvs/demo.csv",
            ),
                },
                },
    assert filtered_csv[0].path.exists()
    df = pd.read_csv(filtered_csv[0].path)


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
                    "-q": "include_this == 'yes'",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    assert filtered_csv[0].path.exists()
    assert filtered_csv[0].uftype == ".any.csv"
    df = pd.read_csv(filtered_csv[0].path)
    assert df.shape[0] == 2


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
                    "-q": None,
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    assert filtered_csv[0].path.exists()
    assert filtered_csv[0].uftype == ".any.csv"
    df = pd.read_csv(filtered_csv[0].path)
    assert df.shape[0] == 3


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
                    "-q": "spectrum_id > 3000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    assert filtered_csv[0].path.exists()
    df = pd.read_csv(filtered_csv[0].path)
    assert df.shape[0] == 8
    assert df["Sequence Start"].sum() == 2142