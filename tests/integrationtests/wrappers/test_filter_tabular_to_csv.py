import pandas as pd



                f"#unified_csvs/demo.csv",
            ),
                },
                },
    assert filtered_csv[0].path.exists()
    df = pd.read_csv(filtered_csv[0].path)


        [
                f"#parquets/demo.parquet",
            ),
        ],
    )
        {
            "parameters": {
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


        [
                f"#parquets/demo.parquet",
            ),
        ],
    )
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


        [
                f"#unified_csvs/demo.csv",
            ),
                f"#xlsx/demo.xlsx",
            ),
        ],
    )
        {
            "parameters": {
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