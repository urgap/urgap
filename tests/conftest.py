import os
import platform
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse
import pytest
import urllib3




def ping(host):
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.

    https://stackoverflow.com/questions/2953462/pinging-servers-in-python
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"

    command = ["ping", param, "1", host]

    return subprocess.call(command) == 0


def init_nodes(ufile_path_list=None, urun_dict=None, unodes=None):
        ufile_path_list = [ufile_path_list]

    for u in ufiles:
        check_ufile_can_be_tested(u)
            urun_dict=urun_dict,
            unode_meta=node_obj.META_INFO,
        )
        for output_file in ut.output_files:


@pytest.fixture
def provide_clean_node_dirs(request):
    unodes, ufiles, urun_dict = init_nodes(
        ufile_path_list=request.param[0],
        urun_dict=request.param[1],
        unodes=request.param[2],
    )
    yield unodes, ufiles, urun_dict
    unodes, ufiles, urun_dict = init_nodes(
        ufile_path_list=request.param[0],
        urun_dict=request.param[1],
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
    check_ufile_can_be_tested(ufile)
    ufile.purge_local()
    yield ufile
    ufile.purge_local()


@pytest.fixture
    if str(request.param[0]) == "mongodb":
        host, port = parsed_url.netloc.split(":")
        try:
            urllib3.util.connection.create_connection((host, port))
        except ConnectionRefusedError:
            pytest.skip(f"MongoDB at {host}:{port} not reachable ...")

    if str(request.param[0]) == "json":
        um.ufile.io.remote_path.parent.mkdir(parents=True, exist_ok=True)
        with open(um.ufile.io.remote_path, "w") as oo:
            print("test", file=oo)

    ufile_path_list = [
    ]
        "parameters": {
            "triggers_nuttin": 100,
            "triggers_rerun": 100,
            "triggers_rerun_-3": 100,
        },
        "unode_parameters": {
            "record_skipped_runs": True,
        },

    if str(request.param[0]) == "json":
        um.ufile.io.remote_path.unlink()