import logging


import pytest

from urgap.ufile.io.azure_datalake import IOAzureDL


@pytest.mark.parametrize("missing_key", ["tenant-id", "client-id"])
def test_init_missing_required_keys(missing_key):
    mock_uuri = MagicMock()
    mock_uuri.query = {"tenant-id": "tid", "client-id": "cid"}
    del mock_uuri.query[missing_key]
    mock_uuri.user = "accountname"

    def fake_init(self, **kwargs):
        self.uuri = kwargs["uuri"]

    with patch("urgap.ufile.io.azure_datalake.UIOBase.__init__", new=fake_init):
        with patch("urgap.ufile.io.azure_datalake.DataLakeServiceClient"):
            with pytest.raises(OSError) as excinfo:
                IOAzureDL(uuri=mock_uuri)
            assert f"DataLake '{missing_key}' was not found in the query!" in str(
                excinfo.value
            )


def test_init_happy_path_builds_available_file_systems():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}
    dummy_uuri.user = "accountname"
    dummy_uuri.password = "secret"
    dummy_uuri.get_azure_share.return_value = "myfs"
    dummy_uuri.get_azure_directory_list.return_value = ["dir1"]
    dummy_uuri.get_azure_object_directory_list.return_value = ["objdir"]
    dummy_uuri.get_azure_object_file.return_value = "file.txt"

    dls_client = MagicMock()
    dls_client.list_file_systems.return_value = [{"name": "myfs"}]
    fs_client = MagicMock()
    dir_client = MagicMock()
    obj_dir_client = MagicMock()
    file_client = MagicMock()
    dls_client.get_file_system_client.return_value = fs_client
    fs_client.get_directory_client.side_effect = [dir_client, obj_dir_client]
    dir_client.get_file_client.return_value = file_client

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]

    with patch("urgap.ufile.io.azure_datalake.UIOBase.__init__", new=dummy_init):
        with patch(
            "urgap.ufile.io.azure_datalake.DataLakeServiceClient",
            return_value=dls_client,
        ):
            with patch("urgap.ufile.io.azure_datalake.ClientSecretCredential"):
                io = IOAzureDL(uuri=dummy_uuri)

    assert isinstance(io, IOAzureDL)
    dls_client.list_file_systems.assert_called_once()
    assert io.file_client == file_client


def test_init_raises_if_share_not_available():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}
    dummy_uuri.user = "accountname"
    dummy_uuri.password = "secret"
    dummy_uuri.get_azure_share.return_value = "missingfs"
    dummy_uuri.netloc = "accountname.dfs.core.windows.net"

    dls_client = MagicMock()
    dls_client.list_file_systems.return_value = [{"name": "otherfs"}]

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]

    with patch("urgap.ufile.io.azure_datalake.UIOBase.__init__", new=dummy_init):
        with patch(
            "urgap.ufile.io.azure_datalake.DataLakeServiceClient",
            return_value=dls_client,
        ):
            with patch("urgap.ufile.io.azure_datalake.ClientSecretCredential"):
                with pytest.raises(OSError) as excinfo:
                    IOAzureDL(uuri=dummy_uuri)

    expected_msg = (
        f"File system 'missingfs' is not available on host {dummy_uuri.netloc}"
        f". Available file systems are: ['otherfs']"
    )
    assert expected_msg in str(excinfo.value)


def test_init_calls_get_file_system_client_with_share():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}
    dummy_uuri.user = "accountname"
    dummy_uuri.password = "secret"
    dummy_uuri.get_azure_share.return_value = "myfs"
    dummy_uuri.get_azure_directory_list.return_value = ["dir1"]
    dummy_uuri.get_azure_object_directory_list.return_value = ["objdir"]
    dummy_uuri.get_azure_object_file.return_value = "file.txt"

    dls_client = MagicMock()
    dls_client.list_file_systems.return_value = [{"name": "myfs"}]
    fs_client = MagicMock()
    dir_client = MagicMock()
    obj_dir_client = MagicMock()
    file_client = MagicMock()

    dls_client.get_file_system_client.return_value = fs_client
    fs_client.get_directory_client.side_effect = [dir_client, obj_dir_client]
    dir_client.get_file_client.return_value = file_client

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]

    with patch("urgap.ufile.io.azure_datalake.UIOBase.__init__", new=dummy_init):
        with patch(
            "urgap.ufile.io.azure_datalake.DataLakeServiceClient",
            return_value=dls_client,
        ):
            with patch("urgap.ufile.io.azure_datalake.ClientSecretCredential"):
                IOAzureDL(uuri=dummy_uuri)

    dls_client.get_file_system_client.assert_called_once_with("myfs")


def test_init_calls_get_directory_client_with_combined_path():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}
    dummy_uuri.user = "accountname"
    dummy_uuri.password = "secret"
    dummy_uuri.get_azure_share.return_value = "myfs"
    dummy_uuri.get_azure_directory_list.return_value = ["dir1"]
    dummy_uuri.get_azure_object_directory_list.return_value = ["objdir"]

    dls_client = MagicMock()
    fs_client = MagicMock()
    directory_client = MagicMock()

    dls_client.list_file_systems.return_value = [{"name": "myfs"}]
    dls_client.get_file_system_client.return_value = fs_client
    fs_client.get_directory_client.return_value = directory_client

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]

    with patch("urgap.ufile.io.azure_datalake.UIOBase.__init__", new=dummy_init):
        with patch(
            "urgap.ufile.io.azure_datalake.DataLakeServiceClient",
            return_value=dls_client,
        ):
            with patch("urgap.ufile.io.azure_datalake.ClientSecretCredential"):
                io_dl = IOAzureDL(uuri=dummy_uuri)

    dls_client.get_file_system_client.assert_called_once_with("myfs")

    expected_path = "/".join(
        dummy_uuri.get_azure_directory_list()
        + dummy_uuri.get_azure_object_directory_list()
    )
    assert (
        call(directory=expected_path) in fs_client.get_directory_client.call_args_list
    )


def test_ioazure_dl_init_calls_clients_correctly():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}
    dummy_uuri.user = "accountname"
    dummy_uuri.password = "secret"
    dummy_uuri.get_azure_share.return_value = "myfs"
    dummy_uuri.get_azure_directory_list.return_value = ["dir1"]
    dummy_uuri.get_azure_object_directory_list.return_value = ["objdir"]
    dummy_uuri.get_azure_object_file.return_value = "file.txt"

    dls_client = MagicMock()
    fs_client = MagicMock()
    directory_client = MagicMock()
    object_directory_client = MagicMock()
    file_client = MagicMock()

    dls_client.list_file_systems.return_value = [{"name": "myfs"}]
    dls_client.get_file_system_client.return_value = fs_client
    fs_client.get_directory_client.side_effect = [
        directory_client,
        object_directory_client,
    ]
    directory_client.get_file_client.return_value = file_client

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]

    with patch("urgap.ufile.io.azure_datalake.UIOBase.__init__", new=dummy_init):
        with patch(
            "urgap.ufile.io.azure_datalake.DataLakeServiceClient",
            return_value=dls_client,
        ):
            with patch("urgap.ufile.io.azure_datalake.ClientSecretCredential"):
                io_dl = IOAzureDL(uuri=dummy_uuri)

    dls_client.get_file_system_client.assert_called_once_with("myfs")

    expected_dir_path = "/".join(
        dummy_uuri.get_azure_directory_list()
        + dummy_uuri.get_azure_object_directory_list()
    )
    expected_obj_dir_path = "/".join(dummy_uuri.get_azure_directory_list())

    fs_client.get_directory_client.assert_has_calls(
        [call(directory=expected_dir_path), call(directory=expected_obj_dir_path)]
    )

    directory_client.get_file_client.assert_called_once_with("file.txt")

    logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
    assert logger.level == logging.ERROR


def test_ioazure_dl_del_deletes_clients():
    dummy_uuri = MagicMock()

    dls_client = MagicMock()
    fs_client = MagicMock()
    directory_client = MagicMock()
    object_directory_client = MagicMock()
    file_client = MagicMock()

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]
        self.datalake_service_client = dls_client
        self.file_system_client = fs_client
        self.directory_client = directory_client
        self.object_directory_client = object_directory_client
        self.file_client = file_client

    with patch.object(IOAzureDL, "__init__", new=dummy_init):
        io_dl = IOAzureDL(uuri=dummy_uuri)

    assert hasattr(io_dl, "file_client")
    assert hasattr(io_dl, "directory_client")
    assert hasattr(io_dl, "file_system_client")
    assert hasattr(io_dl, "datalake_service_client")

    io_dl.__del__()

    for attr in [
        "file_client",
        "directory_client",
        "file_system_client",
        "datalake_service_client",
    ]:
        assert not hasattr(io_dl, attr)