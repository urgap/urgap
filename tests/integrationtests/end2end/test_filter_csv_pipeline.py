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
        {
            "parameters": {
                    "-q": "500 < `exp_mz` < 1000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
        {
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
                "latest_exe_paths": {
                    "CompressToTar:latest": urgap.home
                    / "resources"
                    / "Compressor"
                    / "1_0_0"
                    / "compressor.py",
                },
            },
        },
    )
    assert df["sequence_start"].sum() == 9925
    assert df.shape[0] == 31


        {"-q": "710 < `exp_mz` < 730"},
    )
    )
    assert df["sequence_start"].sum() == 1144
    assert df.shape[0] == 4