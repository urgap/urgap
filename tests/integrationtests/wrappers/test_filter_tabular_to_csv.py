import pandas as pd



                },
    assert filtered_csv[0].path.exists()
    df = pd.read_csv(filtered_csv[0].path)


        [
    )
        {
            "parameters": {
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    assert filtered_csv[0].path.exists()
    assert filtered_csv[0].uftype == ".any.csv"
    df = pd.read_csv(filtered_csv[0].path)
    assert df.shape[0] == 2


        [
    )
        {
            "parameters": {
                    "-q": None,
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    assert filtered_csv[0].path.exists()
    assert filtered_csv[0].uftype == ".any.csv"
    df = pd.read_csv(filtered_csv[0].path)
    assert df.shape[0] == 3


        [
            ),
            ),
    )
        {
            "parameters": {
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    assert filtered_csv[0].path.exists()
    df = pd.read_csv(filtered_csv[0].path)
    assert df.shape[0] == 8
    assert df["Sequence Start"].sum() == 2142