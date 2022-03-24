import pytest


@pytest.mark.parametrize(
    [
        ("mongodb",),
    ],
)
def test_each_pipeline_run_creates_one_wid(
):
    (
        ufiles,
