import pytest



@pytest.fixture
def provide_clean_node_dirs(request):
        ufile_path_list=request.param[0],
        unodes=request.param[2],
    )
        ufile_path_list=request.param[0],
        unodes=request.param[2],
    )


def tmp_dir():




def tmp_scratch_disk(tmp_dir):
    yield tmp_dir