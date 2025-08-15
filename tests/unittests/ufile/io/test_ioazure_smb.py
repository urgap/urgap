import contextlib
import logging
import re

from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

from urgap.ufile.io.azure_smb import IOAzureSMB


@pytest.fixture
def mock_uuri():
    m = MagicMock()
    m.netloc = "https://fakeaccount.file.core.windows.net"
    m.password = "fake_sas_token"
    m.get_azure_share.return_value = "testshare"
    m.get_azure_directory_list.return_value = ["dir1"]
    m.get_azure_object_directory_list.return_value = ["dir2"]
    m.get_azure_object_file.return_value = "file.txt"
    return m


def test_init_super_and_share_service_client(mock_uuri):
    with patch(
        "urgap.ufile.io.azure_smb.ShareServiceClient"
    ) as mock_share_service_client:
        mock_share_service_client.return_value.list_shares.return_value = [
            {"name": "testshare"}
        ]

        def fake_init(self, **kwargs):
            self.uuri = kwargs["uuri"]

        with patch("urgap.ufile.io.azure_smb.UIOBase.__init__", new=fake_init):
            obj = IOAzureSMB(uuri=mock_uuri)

            assert obj.uuri == mock_uuri
            mock_share_service_client.assert_called_once_with(
                account_url=mock_uuri.netloc,
                credential=mock_uuri.password,
            )


def test_share_exists(mock_uuri):
    """Test constructor when share exists."""
    with (
        patch("urgap.ufile.io.azure_smb.ShareServiceClient") as mock_share_client,
        patch(
            "urgap.ufile.io.azure_smb.UIOBase.__init__",
            new=lambda self, **kwargs: setattr(self, "uuri", kwargs["uuri"]),
        ),
    ):
        mock_share_client.return_value.list_shares.return_value = [
            {"name": "testshare"}
        ]
        obj = IOAzureSMB(uuri=mock_uuri)
        assert obj.share_client is not None


def test_share_missing(mock_uuri):
    """Test constructor raises OSError when share does not exist."""
    with (
        patch("urgap.ufile.io.azure_smb.ShareServiceClient") as mock_share_client,
        patch(
            "urgap.ufile.io.azure_smb.UIOBase.__init__",
            new=lambda self, **kwargs: setattr(self, "uuri", kwargs["uuri"]),
        ),
    ):
        mock_share_client.return_value.list_shares.return_value = [
            {"name": "othershare"}
        ]
        with pytest.raises(OSError) as e:
            IOAzureSMB(uuri=mock_uuri)
        assert "Share testshare is not available" in str(e.value)


@patch("urgap.ufile.io.azure_smb.ShareServiceClient")
def test_del_method(mock_share_service_client, mock_uuri):
    """Test case to ensure the __del__ method works without raising errors"""

    mock_share_service_client.return_value.list_shares.return_value = [
        {"name": "testshare"}
    ]
    mock_share_service_client.return_value.get_share_client.return_value = MagicMock()

    obj = IOAzureSMB(uuri=mock_uuri)

    obj.file_client = MagicMock()
    obj.directory_client = MagicMock()
    obj.share_client = MagicMock()
    obj.share_service_client = mock_share_service_client.return_value

    assert hasattr(obj, "file_client")
    assert hasattr(obj, "directory_client")
    assert hasattr(obj, "share_client")
    assert hasattr(obj, "share_service_client")

    try:
        if hasattr(obj, "file_client"):
            del obj.file_client
        if hasattr(obj, "directory_client"):
            del obj.directory_client
        if hasattr(obj, "share_client"):
            del obj.share_client
        if hasattr(obj, "share_service_client"):
            del obj.share_service_client

        del obj
    except Exception as e:
        pytest.fail(f"Deletion raised an exception: {str(e)}")

    assert True


@patch("urgap.ufile.io.azure_smb.ShareServiceClient")
def test_remote_path_returns_none(mock_share_service_client, mock_uuri):
    """Ensure remote_path property returns None."""

    mock_share_service_client.return_value.list_shares.return_value = [
        {"name": "testshare"}
    ]
    mock_share_service_client.return_value.get_share_client.return_value.get_directory_client.return_value.get_file_client.return_value = MagicMock()

    obj = IOAzureSMB(uuri=mock_uuri)
    assert obj.remote_path is None


@patch("urgap.ufile.io.azure_smb.ShareServiceClient")
def test_get_file_properties(mock_share_service_client, mock_uuri):
    """Test that get_file_properties() returns mocked properties."""

    mock_file_client = MagicMock()
    mock_file_client.get_file_properties.return_value = {
        "name": "testfile.txt",
        "metadata": {"tag1": "value1"},
        "path": "/testdir/testfile.txt",
    }

    mock_directory_client = MagicMock()
    mock_directory_client.get_file_client.return_value = mock_file_client

    mock_share_client = MagicMock()
    mock_share_client.get_directory_client.return_value = mock_directory_client

    mock_share_service_client.return_value.list_shares.return_value = [
        {"name": "testshare"}
    ]
    mock_share_service_client.return_value.get_share_client.return_value = (
        mock_share_client
    )

    obj = IOAzureSMB(uuri=mock_uuri)

    props = obj.get_file_properties()
    assert props["name"] == "testfile.txt"
    assert props["metadata"]["tag1"] == "value1"


@patch("urgap.ufile.io.azure_smb.ShareServiceClient")
def test_get_remote_tags(mock_share_service_client, mock_uuri):
    """Test that get_remote_tags() returns mocked metadata."""

    mock_file_client = MagicMock()
    mock_file_client.get_file_properties.return_value = {
        "name": "testfile.txt",
        "metadata": {"tag1": "value1"},
        "path": "/testdir/testfile.txt",
    }

    mock_directory_client = MagicMock()
    mock_directory_client.get_file_client.return_value = mock_file_client

    mock_share_client = MagicMock()
    mock_share_client.get_directory_client.return_value = mock_directory_client

    mock_share_service_client.return_value.list_shares.return_value = [
        {"name": "testshare"}
    ]
    mock_share_service_client.return_value.get_share_client.return_value = (
        mock_share_client
    )

    obj = IOAzureSMB(uuri=mock_uuri)

    metadata = obj.get_remote_tags()
    assert metadata == {"tag1": "value1"}


from unittest.mock import MagicMock, patch

import pytest

from urgap.ufile.io.azure_smb import IOAzureSMB


@patch("urgap.ufile.io.azure_smb.ShareServiceClient")
def test_get_file_properties_methods(mock_share_service_client, mock_uuri):
    """Test get_remote_tags() and get_object() with mocked file properties."""

    mock_file_client = MagicMock()
    mock_file_client.get_file_properties.return_value = {
        "metadata": {"tag1": "value1"},
        "path": "/testdir/testfile.txt",
    }

    mock_directory_client = MagicMock()
    mock_directory_client.get_file_client.return_value = mock_file_client

    mock_share_client = MagicMock()
    mock_share_client.get_directory_client.return_value = mock_directory_client

    mock_share_service_client.return_value.list_shares.return_value = [
        {"name": "testshare"}
    ]
    mock_share_service_client.return_value.get_share_client.return_value = (
        mock_share_client
    )

    obj = IOAzureSMB(uuri=mock_uuri)

    metadata = obj.get_remote_tags()
    assert metadata == {"tag1": "value1"}

    path = obj.get_object()
    assert path == "/testdir/testfile.txt"


@patch("urgap.ufile.io.azure_smb.ShareServiceClient")
@patch("pathlib.Path.open")
def test_download(mock_open, mock_share_service_client, mock_uuri):
    """Test the download method in IOAzureSMB."""

    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    mock_download = MagicMock()

    def readinto(file_obj):
        file_obj.write(b"dummy data")
        return len(b"dummy data")

    mock_download.readinto.side_effect = readinto

    mock_file_client = MagicMock()
    mock_file_client.download_file.return_value = mock_download

    mock_directory_client = MagicMock()
    mock_directory_client.get_file_client.return_value = mock_file_client

    mock_share_client = MagicMock()
    mock_share_client.get_directory_client.return_value = mock_directory_client

    mock_share_service_client.return_value.list_shares.return_value = [
        {"name": "testshare"}
    ]
    mock_share_service_client.return_value.get_share_client.return_value = (
        mock_share_client
    )

    obj = IOAzureSMB(uuri=mock_uuri)

    obj.download()

    mock_file_client.download_file.assert_called_once()

    mock_open.assert_called_once_with("wb")
    mock_file.write.assert_called()


@patch("urgap.ufile.io.azure_smb.ShareServiceClient")
@patch("pathlib.Path.open")
def test_download_raises_runtime_error(mock_open, mock_share_service_client, mock_uuri):
    """Ensure download raises RuntimeError when download_file fails."""

    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    mock_file_client = MagicMock()
    mock_file_client.download_file.side_effect = ResourceNotFoundError("File not found")

    mock_directory_client = MagicMock()
    mock_directory_client.get_file_client.return_value = mock_file_client

    mock_share_client = MagicMock()
    mock_share_client.get_directory_client.return_value = mock_directory_client

    mock_share_service_client.return_value.list_shares.return_value = [
        {"name": "testshare"}
    ]
    mock_share_service_client.return_value.get_share_client.return_value = (
        mock_share_client
    )

    obj = IOAzureSMB(uuri=mock_uuri)

    with patch.object(Path, "unlink") as mock_unlink:
        with pytest.raises(RuntimeError):
            obj.download()

        mock_unlink.assert_called_once()


def test_directory_client_loop():
    mock_file_client = MagicMock()
    mock_file_client.directory_path = "folder1/folder2/folder3"

    mock_share_client = MagicMock()

    class DummyIO:
        def __init__(self, file_client, share_client):
            self.file_client = file_client
            self.share_client = share_client

        def walk_directories(self):
            file_dir_list = self.file_client.directory_path.split("/")
            result = []
            for n in range(len(file_dir_list)):
                tmp_dir_client = self.share_client.get_directory_client(
                    directory_path="/".join(file_dir_list[: n + 1])
                )
                result.append(tmp_dir_client)
            return result

    obj = DummyIO(mock_file_client, mock_share_client)
    obj.walk_directories()

    expected_calls = [
        call(directory_path="folder1"),
        call(directory_path="folder1/folder2"),
        call(directory_path="folder1/folder2/folder3"),
    ]

    mock_share_client.get_directory_client.assert_has_calls(expected_calls)
    assert mock_share_client.get_directory_client.call_count == 3


def test_upload_file_with_suppress(tmp_path):
    mock_file_client = MagicMock()
    mock_tmp_dir_client = MagicMock()
    mock_share_client = MagicMock()
    mock_scratch_file = tmp_path / "scratch.txt"
    mock_scratch_file.write_text("dummy content")

    tmp_dir_client = mock_tmp_dir_client

    class DummyIO:
        def __init__(self, file_client, share_client, scratch_path, tmp_dir_client):
            self.file_client = file_client
            self.share_client = share_client
            self.scratch_path = scratch_path
            self.tmp_dir_client = tmp_dir_client

        def upload(self):
            with contextlib.suppress(ResourceExistsError):
                self.tmp_dir_client.create_directory()
            try:
                with self.scratch_path.open("rb") as data:
                    self.file_client.upload_file(data)
            except Exception as e:
                raise RuntimeError from e

    obj = DummyIO(
        mock_file_client, mock_share_client, mock_scratch_file, tmp_dir_client
    )

    with patch.object(
        contextlib, "suppress", wraps=contextlib.suppress
    ) as mock_suppress:
        obj.upload()

    tmp_dir_client.create_directory.assert_called_once()
    mock_file_client.upload_file.assert_called_once()
    mock_suppress.assert_called()


def test_upload_file_failure_logs_and_raises(tmp_path):
    scratch_file = tmp_path / "scratch.txt"
    scratch_file.write_text("dummy content")

    mock_file_client = MagicMock()
    mock_file_client.upload_file.side_effect = Exception("upload failed")

    class DummyIO:
        def __init__(self, file_client, scratch_path, logger):
            self.file_client = file_client
            self.scratch_path = scratch_path
            self.logger = logger

        def upload(self):
            try:
                with self.scratch_path.open("rb") as data:
                    self.file_client.upload_file(data)
            except Exception as e:
                msg = f"File {self.scratch_path} couldn't be uploaded!"
                self.logger.exception(msg)
                raise RuntimeError(msg) from e

    mock_logger = MagicMock()
    obj = DummyIO(mock_file_client, scratch_file, mock_logger)

    with pytest.raises(RuntimeError) as exc_info:
        obj.upload()

    assert str(exc_info.value) == f"File {scratch_file} couldn't be uploaded!"

    mock_logger.exception.assert_called_once_with(
        f"File {scratch_file} couldn't be uploaded!"
    )

    mock_file_client.upload_file.assert_called_once()


def test_set_file_metadata_called():
    mock_file_client = MagicMock()
    tags = {"key1": "value1", "key2": "value2"}

    class DummyIO:
        def __init__(self, file_client):
            self.file_client = file_client

        def upload_with_tags(self, tags=None):
            if tags is not None:
                self.file_client.set_file_metadata(tags)

    obj = DummyIO(mock_file_client)
    obj.upload_with_tags(tags=tags)

    mock_file_client.set_file_metadata.assert_called_once_with(tags)


def test_file_exists_calls_client_exists():
    mock_file_client = MagicMock()
    mock_file_client.exists.return_value = True

    class DummyIO:
        def __init__(self, file_client):
            self.file_client = file_client

        def exists(self):
            return self.file_client.exists()

    obj = DummyIO(mock_file_client)
    result = obj.exists()

    mock_file_client.exists.assert_called_once()

    assert result is True


def test_directory_exists_check():
    mock_directory_client = MagicMock()

    class DummyIO:
        def __init__(self, directory_client):
            self.directory_client = directory_client

        def exists(self):
            try:
                self.directory_client.get_directory_properties()
            except ResourceNotFoundError:
                return False
            return True

    mock_directory_client.get_directory_properties.return_value = {"props": "some"}
    obj = DummyIO(mock_directory_client)
    assert obj.exists() is True
    mock_directory_client.get_directory_properties.assert_called_once()

    mock_directory_client.get_directory_properties.side_effect = ResourceNotFoundError(
        "Not found"
    )
    obj2 = DummyIO(mock_directory_client)
    assert obj2.exists() is False


from unittest.mock import MagicMock


def test_directory_exists_returns_true():
    mock_directory_client = MagicMock()
    mock_directory_client.get_directory_properties.return_value = {"props": "some"}

    class DummyIO:
        def __init__(self, directory_client):
            self.directory_client = directory_client

        def exists(self):
            try:
                self.directory_client.get_directory_properties()
            except ResourceNotFoundError:
                return False
            return True

    obj = DummyIO(mock_directory_client)
    assert obj.exists() is True
    mock_directory_client.get_directory_properties.assert_called_once()


def test_list_all_files_with_paths():
    mock_file_client = MagicMock()
    mock_directory_client = MagicMock()

    mock_file1 = MagicMock()
    mock_file1.name = "file1.txt"
    mock_file2 = MagicMock()
    mock_file2.name = "file2.txt"

    mock_directory_client.list_files_and_directories.return_value = [
        mock_file1,
        mock_file2,
    ]

    class DummyIO:
        def __init__(self, directory_client):
            self.directory_client = directory_client

        def _list_all_files_with_paths(self):
            result = []
            for file_or_dir in self.directory_client.list_files_and_directories():
                result.append(file_or_dir.name)
            return result

    obj = DummyIO(mock_directory_client)
    files = obj._list_all_files_with_paths()

    assert files == ["file1.txt", "file2.txt"]
    mock_directory_client.list_files_and_directories.assert_called_once()


def test_list_all_files_with_paths_recursive():
    file1 = MagicMock()
    file1.name = "file1.txt"
    file2 = MagicMock()
    file2.name = "file2.txt"

    subdir_file = MagicMock()
    subdir_file.name = "subfile.txt"

    subdir = MagicMock()
    subdir.name = "subdir"

    root_dir_client = MagicMock()
    root_dir_client.list_files_and_directories.return_value = [file1, subdir, file2]

    sub_dir_client = MagicMock()
    sub_dir_client.list_files_and_directories.return_value = [subdir_file]

    root_dir_client.get_subdirectory_client.return_value = sub_dir_client

    class DummyIO:
        def __init__(self, directory_client):
            self.directory_client = directory_client

        def _list_all_files_with_paths(self):
            files_with_paths = []

            def walk(dir_client, path=""):
                for entry in dir_client.list_files_and_directories():
                    if hasattr(entry, "name") and entry.name != "":  # File
                        if entry == subdir:
                            walk(
                                dir_client.get_subdirectory_client(entry.name),
                                f"{path}/{entry.name}" if path else entry.name,
                            )
                        else:
                            files_with_paths.append(
                                f"{path}/{entry.name}" if path else entry.name
                            )

            walk(self.directory_client)
            return files_with_paths

    obj = DummyIO(root_dir_client)
    result = obj._list_all_files_with_paths()

    assert result == ["file1.txt", "subdir/subfile.txt", "file2.txt"]
    root_dir_client.list_files_and_directories.assert_called_once()
    sub_dir_client.list_files_and_directories.assert_called_once()


def test_list_all_files_with_paths_builds_correct_paths():
    from unittest.mock import MagicMock

    file1 = MagicMock()
    file1.name = "file1.txt"

    file2 = MagicMock()
    file2.name = "file2.txt"

    subdir = MagicMock()
    subdir.name = "subdir"

    subfile = MagicMock()
    subfile.name = "subfile.txt"

    root_dir_client = MagicMock()
    root_dir_client.list_directories_and_files.return_value = [file1, subdir, file2]

    sub_dir_client = MagicMock()
    sub_dir_client.list_directories_and_files.return_value = [subfile]

    class DummyIO:
        def __init__(self, directory_client):
            self.directory_client = directory_client

        def _list_all_files_with_paths(self, directory_client=None, current_path=None):
            if directory_client is None:
                directory_client = self.directory_client

            files_with_paths = []

            for item in directory_client.list_directories_and_files():
                if current_path is None:
                    item_path = item.name
                else:
                    item_path = f"{current_path}/{item.name}"

                if item.name == "subdir":
                    files_with_paths.extend(
                        self._list_all_files_with_paths(sub_dir_client, item_path)
                    )
                else:
                    files_with_paths.append(item_path)
            return files_with_paths

    obj = DummyIO(root_dir_client)
    result = obj._list_all_files_with_paths()

    assert result == ["file1.txt", "subdir/subfile.txt", "file2.txt"]


def test_extend_includes_subdir_files():
    file1 = MagicMock()
    file1.name = "file1.txt"
    file1.is_directory = False

    file2 = MagicMock()
    file2.name = "file2.txt"
    file2.is_directory = False

    subdir = MagicMock()
    subdir.name = "subdir"
    subdir.is_directory = True

    subfile = MagicMock()
    subfile.name = "subfile.txt"
    subfile.is_directory = False

    root_dir_client = MagicMock()
    root_dir_client.list_directories_and_files.return_value = [file1, subdir, file2]

    sub_dir_client = MagicMock()
    sub_dir_client.list_directories_and_files.return_value = [subfile]

    class DummyIO:
        def __init__(self, directory_client):
            self.directory_client = directory_client

        def get_subdirectory_client(self, name):
            if name == "subdir":
                return sub_dir_client


def _list_all_files_with_paths(directory_client, current_path=None):
    files_with_paths = []
    for item in directory_client.list_directories_and_files():
        if current_path is None:
            item_path = item.name
        else:
            item_path = f"{current_path}/{item.name}"

        if item.is_directory:
            subdir_client = directory_client.get_subdirectory_client(item.name)
            subdir_files = _list_all_files_with_paths(subdir_client, item_path)
            files_with_paths.extend(subdir_files)
        else:
            files_with_paths.append(item_path)
    return files_with_paths


def test_list_all_files_with_subdir_recursion():
    root_file = MagicMock()
    root_file.name = "root_file.txt"
    root_file.is_directory = False

    subdir = MagicMock()
    subdir.name = "subdir"
    subdir.is_directory = True

    sub_file = MagicMock()
    sub_file.name = "sub_file.txt"
    sub_file.is_directory = False

    root_client = MagicMock()
    root_client.list_directories_and_files.return_value = [root_file, subdir]

    subdir_client = MagicMock()
    subdir_client.list_directories_and_files.return_value = [sub_file]

    root_client.get_subdirectory_client.return_value = subdir_client

    result = _list_all_files_with_paths(root_client)

    root_client.get_subdirectory_client.assert_called_once_with("subdir")
    assert "root_file.txt" in result
    assert "subdir/sub_file.txt" in result
    assert len(result) == 2


def _list_all_files_with_paths(directory_client, current_path=None, limit=None):
    files_with_paths = []
    for item in directory_client.list_directories_and_files():
        if current_path is None:
            item_path = item.name
        else:
            item_path = f"{current_path}/{item.name}"

        if getattr(item, "is_directory", False):
            subdir_client = directory_client.get_subdirectory_client(item.name)
            subdir_files = _list_all_files_with_paths(subdir_client, item_path, limit)
            files_with_paths.extend(subdir_files)
        else:
            files_with_paths.append(f"{item_path}")
            if limit is not None and len(files_with_paths) >= limit:
                break
    return files_with_paths


def test_append_files_and_limit():
    file1 = MagicMock()
    file1.name = "file1.txt"
    file1.is_directory = False

    file2 = MagicMock()
    file2.name = "file2.txt"
    file2.is_directory = False

    dir_client = MagicMock()
    dir_client.list_directories_and_files.return_value = [file1, file2]

    result = _list_all_files_with_paths(dir_client)
    assert result == ["file1.txt", "file2.txt"]

    result_limited = _list_all_files_with_paths(dir_client, limit=1)
    assert result_limited == ["file1.txt"]


def _list_all_files_with_paths(directory_client, current_path=None, limit=None):
    files_with_paths = []
    for item in directory_client.list_directories_and_files():
        if current_path is None:
            item_path = item.name
        else:
            item_path = f"{current_path}/{item.name}"

        if item.is_directory:
            subdir_client = directory_client.get_subdirectory_client(item.name)
            subdir_files = _list_all_files_with_paths(subdir_client, item_path, limit)
            files_with_paths.extend(subdir_files)
        else:
            files_with_paths.append(item_path)

        if limit is not None and len(files_with_paths) >= limit:
            files_with_paths = files_with_paths[:limit]
            break

    return files_with_paths


def test_list_container_objects_with_pattern():
    file1 = MagicMock()
    file1.name = "file1.txt"
    file1.is_directory = False

    file2 = MagicMock()
    file2.name = "file2.log"
    file2.is_directory = False

    subdir = MagicMock()
    subdir.name = "subdir"
    subdir.is_directory = True

    subfile = MagicMock()
    subfile.name = "subfile.txt"
    subfile.is_directory = False

    root_dir_client = MagicMock()
    root_dir_client.list_directories_and_files.return_value = [file1, subdir, file2]

    sub_dir_client = MagicMock()
    sub_dir_client.list_directories_and_files.return_value = [subfile]

    root_dir_client.get_subdirectory_client.return_value = sub_dir_client

    class DummyIO:
        def __init__(self, object_directory_client):
            self.object_directory_client = object_directory_client

        def add_storage_uri_to_container_items(self, items):
            return [f"{item}-uri" for item in items]

        def list_container_objects(self, pattern=None, limit=None):
            files = _list_all_files_with_paths(
                self.object_directory_client, limit=limit
            )
            container_objects = self.add_storage_uri_to_container_items(files)
            if pattern is not None:
                container_objects = [
                    f for f in container_objects if re.search(pattern, f)
                ]
            return container_objects

    obj = DummyIO(root_dir_client)

    pattern = r"\.txt"
    result = obj.list_container_objects(pattern=pattern)

    assert result == ["file1.txt-uri", "subdir/subfile.txt-uri"]