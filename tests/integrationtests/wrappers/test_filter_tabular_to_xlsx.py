import pandas as pd

import urgap


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
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    filtered_xlsx = FilterTabularToXlsx_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_xlsx[0].path.exists()
    df = pd.read_excel(filtered_xlsx[0].path)


    ufiles = urgap.UFileList(
        [
            urgap.UFile(
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
    filtered_xlsx = FilterTabularToXlsx_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_xlsx[0].path.exists()
    df = pd.read_excel(filtered_xlsx[0].path)
    assert df.shape[0] == 4
    assert df["Sequence Start"].sum() == 1071


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
                    "-q": "`spectrum_id` > 3000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    filtered_xlsx = FilterTabularToXlsx_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_xlsx[0].path.exists()
    df = pd.read_excel(filtered_xlsx[0].path)