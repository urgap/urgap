import pytest


@pytest.mark.parametrize(
    "provide_clean_node_dirs",
    [
        (
            ),
    ],
    indirect=["provide_clean_node_dirs"],
)
    nodes, ufiles, urun_dict = provide_clean_node_dirs
    filtered_csv = csv_filter_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert filtered_csv[0].path.exists()