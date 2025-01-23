import pytest



@pytest.mark.parametrize(
    "provide_clean_node_dirs",
    [
        (
            ),
                {
                    "parameters": {
                        "FilterTabularToCSV:1.0.0": {
                            "-q": "`spectrum_id` > 3000",
                    },
                    "unode_parameters": {
                        "force": True,
                    },
            ),
            ["FilterTabularToCSV:1.0.0"],
    ],
    indirect=["provide_clean_node_dirs"],
)
    nodes, ufiles, urun_dict = provide_clean_node_dirs
    csv_filter_node = nodes["FilterTabularToCSV:1.0.0"]
    filtered_csv = csv_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_csv[0].path.exists()