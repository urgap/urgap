import pytest


@pytest.mark.parametrize(
    "provide_clean_node_dirs",
    [
        (
            ),
    ],
    indirect=["provide_clean_node_dirs"],
)
    assert filtered_csv[0].path.exists()