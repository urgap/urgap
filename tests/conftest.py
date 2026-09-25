import asyncio
import logging
import os
import platform
import shutil
import socket
import subprocess
import tempfile
import time

from pathlib import Path
from urllib.parse import urlparse

import pytest
import urllib3
import urgap

urgap._test_folder = Path(__file__).parent.resolve()


def ping(host):
    """Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.

    https://stackoverflow.com/questions/2953462/pinging-servers-in-python
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"

    command = ["ping", param, "1", host]

    return subprocess.call(command) == 0


def check_ufile_can_be_tested(ufile):
    """
    Stub function to validate that a UFile object can be tested.
    Replace this logic with actual validation if needed.
    """
    if not isinstance(ufile, urgap.UFile):
        raise TypeError(f"Expected UFile, got {type(ufile)}")


@pytest.fixture
def check_if_ufilelist_can_be_tested(request):
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
        except (TimeoutError, ConnectionRefusedError):
            pytest.skip(f"{umeta_interface} at {host}:{port} not reachable ...")
    return request.param


def init_nodes(ufile_path_list=None, urun_dict=None, unodes=None):
    if isinstance(ufile_path_list, urgap.UFile) is True:
        check_ufile_can_be_tested(ufile_path_list)
        ufile_path_list = [ufile_path_list]
    ufiles = urgap.UFileList(ufile_path_list)
    unodes_dict = {}
    for node in unodes:
        unodes_dict[node] = urgap.init_unode(node)
        if unodes_dict[node].resource_is_available is False:
            pytest.skip(f"{node} is missing resources ...")
        if unodes_dict[node].has_all_required_installations() is False:
            pytest.skip(f"{node} is missing 3rd party installation ...")

    for u in ufiles:
        check_ufile_can_be_tested(u)
    for node_name, node_obj in unodes_dict.items():
        ut = urgap.UTrace(
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
    urun_dict.unode_parameters["storage_base_uri"] = f"file://{tmp_dir_name.name}"
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


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_test_dir_path = Path(tmp_dir) / "tmp_test_dir"
        tmp_test_dir_path.mkdir(exist_ok=True)
        yield tmp_test_dir_path


@pytest.fixture
def tmp_file():
    with tempfile.NamedTemporaryFile() as tmp_file:
        yield Path(tmp_file.name)


@pytest.fixture
def tmp_scratch_disk(tmp_dir):
    urgap.scratch_disk = urgap.uinit.set_scratch_disk_path(tmp_dir)
    yield tmp_dir
    urgap.scratch_disk = urgap.uinit.set_scratch_disk_path()


@pytest.fixture
def change_hash_algorithm():
    urgap.config["hash_algorithm"] = "Argon2"
    yield None
    urgap.config["hash_algorithm"] = "md5"


@pytest.fixture
def provide_clean_scratch_and_remote(request):
    ufile = request.param
    check_ufile_can_be_tested(ufile)
    ufile.purge_local()
    yield ufile
    ufile.purge_local()


@pytest.fixture
def provide_standard_TestNode1_setup_and_set_umeta_interface(request):
    if str(request.param[0]) == "mongodb":
        print(urgap.config)
        parsed_url = urlparse("mongodb://localhost:27017")
        host, port = parsed_url.netloc.split(":")
        try:
            urllib3.util.connection.create_connection((host, port))
        except ConnectionRefusedError:
            pytest.skip(f"MongoDB at {host}:{port} not reachable ...")

    um = urgap.UMeta(io=str(request.param[0]))
    if str(request.param[0]) == "json":
        um.ufile.io.remote_path.parent.mkdir(parents=True, exist_ok=True)
        with open(um.ufile.io.remote_path, "w") as oo:
            print("test", file=oo)

    ufile_path_list = [
        urgap.UFile(
            uri=f"file://{urgap._test_folder}/data#"
            f"test_node_data/test.txt?uftype={urgap.uftypes.test.TEST_FILE1}",
        ),
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


@pytest.fixture
def provide_changeable_config():
    default = urgap.home / "urgap.json"
    backup = urgap.home / "backup_config.json"
    shutil.copy(default, backup)
    yield None
    shutil.copy(backup, default)
    os.remove(backup)


@pytest.fixture
def provide_changeable_credentials():
    default = urgap.home / "credentials_lookup.json"
    backup = urgap.home / "backup_credentials.json"
    shutil.copy(default, backup)
    yield None
    shutil.copy(backup, default)
    os.remove(backup)


@pytest.fixture
def provide_uctl_server(request):
    call = ["uctl", "run", "upi-server"]
    required_ports = []
    if isinstance(request.param, str):
        unode = request.param
        call.extend(["-n", unode])
        required_ports.append(urgap.instances.unode_manager.unode_port_mapping[unode])
    else:
        for param in request.param:
            if isinstance(param, int):
                call.extend(["-m", str(param)])
                required_ports.append(param)
                continue
            call.extend(["-n", param])
            required_ports.append(
                urgap.instances.unode_manager.unode_port_mapping[param],
            )
    proc = subprocess.Popen(call)
    for _ in range(30):
        if all(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(
                ("127.0.0.1", port),
            )
            == 0
            for port in required_ports
        ):
            break
        time.sleep(1)
    yield None
    proc.terminate()


@pytest.fixture(scope="function")
def provide_mcp_tools_server(request):
    call = ["uctl", "run", "mcp-server"]
    port = request.param
    call.extend(["-p", str(port)])
    proc = subprocess.Popen(call)
    for _ in range(30):
        if all(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(
                ("127.0.0.1", p),
            )
            == 0
            for p in [port]
        ):
            break
        time.sleep(1)
    yield None
    proc.terminate()


@pytest.fixture(autouse=True)
def set_caplog_level(caplog):
    caplog.set_level(logging.DEBUG)
