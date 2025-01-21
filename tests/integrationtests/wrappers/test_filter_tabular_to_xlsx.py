import pandas as pd



        [
    )
        {
            "parameters": {
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    assert filtered_xlsx[0].path.exists()
    df = pd.read_excel(filtered_xlsx[0].path)


        [
    )
        {
            "parameters": {
                    "-q": "`spectrum_id` > 3000",
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    assert filtered_xlsx[0].path.exists()
    df = pd.read_excel(filtered_xlsx[0].path)
    assert df.shape[0] == 4
    assert df["Sequence Start"].sum() == 1071


        [
    )
        {
            "parameters": {
                    "-q": "`spectrum_id` > 3000",
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    assert filtered_xlsx[0].path.exists()
    df = pd.read_excel(filtered_xlsx[0].path)