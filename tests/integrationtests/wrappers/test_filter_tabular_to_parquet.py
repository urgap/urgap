import pandas as pd

import urgap


    ufiles = urgap.UFileList(
        [
            urgap.UFile(
            ),
    )
                },
            },
                },
            },
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.PARQUET}"
                f"#parquets/demo.parquet",
            ),
    )
            },
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.PARQUET}"
                f"#parquets/demo.parquet",
            ),
        ],
    )
            },
    )
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


    ufiles = urgap.UFileList(
        [
            urgap.UFile(
            ),
        ],
    )
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


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
                    "-q": "`spectrum_id` > 3000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)
    assert df.shape[0] == 8
    assert df["Sequence Start"].sum() == 2142