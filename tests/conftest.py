import tempfile
from pathlib import Path
import pytest



        ufile_path_list = [ufile_path_list]

    for u in ufiles:
        )

@pytest.fixture
def provide_clean_node_dirs(request):
        ufile_path_list=request.param[0],
        unodes=request.param[2],
    )
        ufile_path_list=request.param[0],
        unodes=request.param[2],
    )


def tmp_dir():
    with tempfile.TemporaryDirectory() as tmp_dir:


def tmp_file():
    with tempfile.NamedTemporaryFile() as tmp_file:
        yield Path(tmp_file.name)


def tmp_scratch_disk(tmp_dir):
    yield tmp_dir


def change_hash_algorithm():
    yield None


@pytest.fixture
def provide_clean_scratch_and_remote(request):
    ufile = request.param
    ufile.purge_local()
    yield ufile
    ufile.purge_local()