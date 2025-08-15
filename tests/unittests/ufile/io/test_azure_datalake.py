import contextlib
import logging

from unittest.mock import MagicMock, PropertyMock, call, patch

import pytest

from azure.core.exceptions import (
    AzureError,  # <-- add this
    ResourceExistsError,
)

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


def test_remote_path_returns_none():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]

    with patch("urgap.ufile.io.azure_datalake.IOAzureDL.__init__", new=dummy_init):
        io_dl = IOAzureDL(uuri=dummy_uuri)

    assert io_dl.remote_path is None


def test_get_file_properties_returns_expected():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}

    file_client = MagicMock()
    expected_props = {"size": 12345}
    file_client.get_file_properties.return_value = expected_props

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]
        self.file_client = file_client

    with patch("urgap.ufile.io.azure_datalake.IOAzureDL.__init__", new=dummy_init):
        io_dl = IOAzureDL(uuri=dummy_uuri)

        io_dl.remote_object_exists = MagicMock(return_value=True)

        result = io_dl.get_file_properties()
        assert result == expected_props
        file_client.get_file_properties.assert_called_once()

        io_dl.remote_object_exists.return_value = False
        assert io_dl.get_file_properties() is None


def test_get_file_metadata_returns_expected():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}

    file_props = {"metadata": {"key1": "value1"}}

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]

    with patch("urgap.ufile.io.azure_datalake.IOAzureDL.__init__", new=dummy_init):
        io_dl = IOAzureDL(uuri=dummy_uuri)

        io_dl.remote_object_exists = MagicMock(return_value=True)
        io_dl.get_file_properties = MagicMock(return_value=file_props)

        result = io_dl.get_remote_tags()

        assert result == {"key1": "value1"}


def test_get_object_returns_expected():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}

    file_props = {"name": "test_file.txt"}

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]

    with patch("urgap.ufile.io.azure_datalake.IOAzureDL.__init__", new=dummy_init):
        io_dl = IOAzureDL(uuri=dummy_uuri)

        io_dl.remote_object_exists = MagicMock(return_value=True)
        io_dl.get_file_properties = MagicMock(return_value=file_props)

        result = io_dl.get_object()
        assert result == "test_file.txt"


def test_download_calls_readinto():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]
        self.file_client = MagicMock()

    with patch("urgap.ufile.io.azure_datalake.IOAzureDL.__init__", new=dummy_init):
        io_dl = IOAzureDL(uuri=dummy_uuri)

        mock_file = MagicMock()
        with patch.object(
            type(io_dl),
            "scratch_path",
            new_callable=PropertyMock,
            return_value=mock_file,
        ):
            mock_download = MagicMock()
            io_dl.file_client.download_file.return_value = mock_download

            io_dl.download()

            io_dl.file_client.download_file.assert_called_once()
            mock_download.readinto.assert_called_once_with(mock_file.open().__enter__())


def test_download_handles_exceptions():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]
        self.file_client = MagicMock()

    with patch("urgap.ufile.io.azure_datalake.IOAzureDL.__init__", new=dummy_init):
        io_dl = IOAzureDL(uuri=dummy_uuri)

        mock_scratch = MagicMock()
        with patch.object(
            type(io_dl),
            "scratch_path",
            new_callable=PropertyMock,
            return_value=mock_scratch,
        ):
            io_dl.file_client.download_file.side_effect = AzureError(
                "Simulated download error"
            )

            with pytest.raises(RuntimeError) as exc_info:
                io_dl.download()

            assert isinstance(exc_info.value.__cause__, AzureError)
            assert str(exc_info.value.__cause__) == "Simulated download error"


def test_get_directory_clients_called_for_each_level():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]
        self.file_client = MagicMock()
        self.file_system_client = MagicMock()

        self.file_client.path_name = "a/b/c/file.txt"

    with patch("urgap.ufile.io.azure_datalake.IOAzureDL.__init__", new=dummy_init):
        io_dl = IOAzureDL(uuri=dummy_uuri)

        io_dl.file_system_client.get_directory_client = MagicMock()

        file_dir_list = io_dl.file_client.path_name.split("/")[:-1]
        for n in range(len(file_dir_list)):
            tmp_dir_client = io_dl.file_system_client.get_directory_client(
                directory="/".join(file_dir_list[: n + 1]),
            )

        expected_calls = [("a",), ("a/b",), ("a/b/c",)]
        actual_calls = [
            call_args[1]["directory"]
            for call_args in io_dl.file_system_client.get_directory_client.call_args_list
        ]
        assert actual_calls == ["a", "a/b", "a/b/c"]


def test_create_directories_and_files_handles_resource_exists():
    dummy_uuri = MagicMock()
    dummy_uuri.query = {"tenant-id": "tid", "client-id": "cid"}

    def dummy_init(self, **kwargs):
        self.uuri = kwargs["uuri"]
        self.file_client = MagicMock()
        self.file_system_client = MagicMock()
        self.client_keys = ["key1", "key2"]
        self.file_client.path_name = "dir1/dir2/file.txt"

    with patch("urgap.ufile.io.azure_datalake.IOAzureDL.__init__", new=dummy_init):
        io_dl = IOAzureDL(uuri=dummy_uuri)

        mock_dir_client = MagicMock()
        mock_dir_client.create_directory.side_effect = [
            ResourceExistsError("exists"),
            None,
            None,
        ]
        io_dl.file_system_client.get_directory_client = MagicMock(
            return_value=mock_dir_client
        )

        io_dl.file_client.create_file = MagicMock()

        tags = {"key1": "val1", "key2": "val2", "other": "val3"}

        file_dir_list = io_dl.file_client.path_name.split("/")[:-1]
        for n in range(len(file_dir_list)):
            tmp_dir_client = io_dl.file_system_client.get_directory_client(
                directory="/".join(file_dir_list[: n + 1]),
            )
            with contextlib.suppress(ResourceExistsError):
                tmp_dir_client.create_directory()

        io_dl.file_client.create_file()
        for keyname in io_dl.client_keys:
            if tags is not None:
                tags.pop(keyname, None)

        io_dl.file_system_client.get_directory_client.assert_called()
        assert io_dl.file_client.create_file.called
        assert "key1" not in tags
        assert "key2" not in tags
        assert "other" in tags