

        [
    )
                },
                },
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


        [
    )
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


    )
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


        [
    )
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)


        [
            ),
            ),
    )
        {
            "parameters": {
                    "-q": "`spectrum_id` > 3000",
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    filtered_parquet = parquet_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_parquet[0].path.exists()
    df = pd.read_parquet(filtered_parquet[0].path)
    assert df.shape[0] == 8
    assert df["Sequence Start"].sum() == 2142