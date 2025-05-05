import networkx



        f"unified_csvs/demo.csv",
    )

        ucfs=input_file.ucfs,
        storage_base_uri=input_file.as_storage_base_uri(),
    )
    assert isinstance(ur.graph, networkx.classes.digraph.DiGraph) is True

        {
            "parameters": {"FilterTabularToCSV:1.0.0": {"-q": "`spectrum_id` < 3000"}},
    )
    filtered_1 = filter_node.run(
        ufiles=[input_file],
        urun_dict=urun_dict,
    )

    urun_dict["parameters"] = {
        "FilterTabularToCSV:1.0.0": {
            "-q": "450 < `Exp m/z` < 600",
    }
    filtered_1b = filter_node.run(
        ufiles=[input_file],
        urun_dict=urun_dict,
    )

    urun_dict["parameters"] = {
        "FilterTabularToCSV:1.0.0": {
            "-q": "`spectrum_id` > 2500",
    }
    filtered_1c = filter_node.run(
        ufiles=filtered_1b,
        urun_dict=urun_dict,
    )

    urun_dict["parameters"] = {
        "FilterTabularToCSV:1.0.0": {
            "-q": "`spectrum_id` > 3000",
    }
    filtered_2 = filter_node.run(
        ufiles=[filtered_1, filtered_1c, input_file],
        urun_dict=urun_dict,
    )

        ucfs=filtered_2[0].ucfs,
        storage_base_uri=filtered_2[0].as_storage_base_uri(),
    )
    assert len(ur.graph.nodes) == 9