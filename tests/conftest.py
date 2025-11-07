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

import libcloud
import pytest
import urllib3

import urgap

urgap._test_folder = Path(__file__).parent.resolve()


def ping(host):
    """Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.

    https://stackoverflow.com/questions/2953462/pinging-servers-in-python
    """
    # Option for the number of packets as a function of
    param = "-n" if platform.system().lower() == "windows" else "-c"

    # Building the command. Ex: "ping -c 1 google.com"
    command = ["ping", param, "1", host]

    return subprocess.call(command) == 0


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


def check_ufile_can_be_tested(u):
    if u.uuri.scheme in ["gcs-libcloud", "minio-libcloud", "local-libcloud"]:
        if u.uuri.password is None:
            pytest.skip("No credentials set in ENVs")

        try:
            if u.io.driver is None:
                pytest.skip("Libcloud could not connect to server")
        except OSError:
            pytest.skip("Auth per cmdline is not supported")

        try:
            u.io.driver.list_containers()
        except libcloud.common.types.InvalidCredsError:
            pytest.skip("Credentials are wrong")

        if u.uuri.scheme == "minio-libcloud":
            try:
                urllib3.util.connection.create_connection((u.uuri.host, u.uuri.port))
            except ConnectionRefusedError:
                pytest.skip("Sever {host}:{port} not reachable ...".format(**u.uuri))
            if os.environ.get("uuser_minio", None) is None:
                pytest.skip("No minio-libcloud password found")

        # if u.uuri.scheme == "gcs-libcloud":
        #     if ping("storage.googleapis.com") is False:
        #         pytest.skip("GCP not reachable")

    if u.uuri.scheme in ["gcs-libcloud", "minio-libcloud", "local-libcloud"]:
        if urgap.config.get("umeta", "json") not in ["mongodb", "tinydb"]:
            pytest.skip(
                "Not right umeta was set. Require decentralized, e.g. mongodb or tinydb",
            )


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
    # cleanup
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
    # os.environ["LIBCLOUD_RETRY_FAILED_HTTP_REQUESTS"] = False
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
        parsed_url = urlparse(urgap.config["umeta-mongodb-url"])
        host, port = parsed_url.netloc.split(":")
        try:
            urllib3.util.connection.create_connection((host, port))
        except ConnectionRefusedError:
            pytest.skip(f"MongoDB at {host}:{port} not reachable ...")

    um = urgap.UMeta(io=str(request.param[0]))
    if str(request.param[0]) == "json":
        # we need to create a temp file
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
                call.extend(["--mcp", str(param)])
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


@pytest.fixture(autouse=True)
def set_caplog_level(caplog):
    caplog.set_level(logging.DEBUG)
