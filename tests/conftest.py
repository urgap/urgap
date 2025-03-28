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


@pytest.fixture
    for u in request.param:
        check_ufile_can_be_tested(u)
    return request.param


@pytest.fixture
def check_if_meta_interface_backend_is_available(request):
    umeta_interface, netloc = request.param
    if netloc is not None:
        parsed_url = urlparse(netloc)
        host, port = parsed_url.netloc.split(":")
        try:
            urllib3.util.connection.create_connection((host, port), timeout=1)
            pytest.skip(f"{umeta_interface} at {host}:{port} not reachable ...")
    return request.param


def init_nodes(ufile_path_list=None, urun_dict=None, unodes=None):
        ufile_path_list = [ufile_path_list]
    unodes_dict = {}
    for node in unodes:
        if unodes_dict[node].resource_is_available is False:
            pytest.skip(f"{node} is missing resources ...")
        if unodes_dict[node].has_all_required_installations() is False:
            pytest.skip(f"{node} is missing 3rd party installation ...")

    for u in ufiles:
        check_ufile_can_be_tested(u)
    for node_name, node_obj in unodes_dict.items():
            urun_dict=urun_dict,
            input_files=ufiles,
            unode_meta=node_obj.META_INFO,
        )
        for output_file in ut.output_files:
            output_file.remove_remote_object()
    return unodes_dict, ufiles, urun_dict

@pytest.fixture
def provide_clean_test_node_dirs(request):
    unodes, ufiles, urun_dict = init_nodes(
        ufile_path_list=request.param[0],
        urun_dict=request.param[1],
        unodes=request.param[2],
    )
    tmp_dir_name = tempfile.TemporaryDirectory()
    yield unodes, ufiles, urun_dict
    tmp_dir_name.cleanup()
    unodes, ufiles, urun_dict = init_nodes(
        ufile_path_list=request.param[0],
        urun_dict=request.param[1],
        unodes=request.param[2],
    )


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
    run_dict = {
        "parameters": {
            "triggers_nuttin": 100,
            "triggers_rerun": 100,
            "triggers_rerun_-3": 100,
        },
        "unode_parameters": {
            "record_skipped_runs": True,
        },
    }
    yield ufile_path_list, run_dict

    if str(request.param[0]) == "json":
        um.ufile.io.remote_path.unlink()


def provide_changeable_config():
    shutil.copy(default, backup)
    yield None
    shutil.copy(backup, default)
    os.remove(backup)


def provide_changeable_credentials():
    shutil.copy(default, backup)
    yield None
    shutil.copy(backup, default)
    os.remove(backup)


@pytest.fixture
def provide_uctl_server(request):
        call.extend(["-n", unode])
    proc = subprocess.Popen(call)
    yield None
    proc.terminate()