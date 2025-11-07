from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from urgap.ufile.io.azure_blob import IOAzureBlobStorage


@pytest.fixture
def dummy_uuri(tmp_path):
    class DummyUURI:
        user = "dummyuser"
        password = "dummypass"
        fragment = "test_blob"

        def get_container_name(self):
            return "test-container"

        def get_object_name(self):
            return "test-object"

    return DummyUURI()


def test_ioazure_init(monkeypatch, dummy_uuri, tmp_path):
    mock_client = MagicMock()
    monkeypatch.setattr(
        "urgap.ufile.io.azure_blob.BlobServiceClient", lambda **kwargs: mock_client
    )

    io_obj = IOAzureBlobStorage(uuri=dummy_uuri)

    monkeypatch.setattr(
        type(io_obj), "scratch_path", property(lambda self: tmp_path / "scratch.txt")
    )

    assert io_obj.client == mock_client
    assert io_obj.container is not None
    assert io_obj.blob is not None


def test_remote_path_property(monkeypatch, dummy_uuri):
    monkeypatch.setattr(
        "urgap.ufile.io.azure_blob.BlobServiceClient", lambda **kwargs: MagicMock()
    )

    io_obj = IOAzureBlobStorage(uuri=dummy_uuri)

    assert io_obj.remote_path is None


def test_get_remote_tags(monkeypatch, dummy_uuri):
    from unittest.mock import MagicMock

    mock_blob_client = MagicMock()
    mock_blob_client.get_blob_properties.return_value = {"metadata": {"key": "value"}}

    mock_container_client = MagicMock()
    mock_container_client.get_blob_client.return_value = mock_blob_client

    mock_service_client = MagicMock()
    mock_service_client.get_container_client.return_value = mock_container_client

    monkeypatch.setattr(
        "urgap.ufile.io.azure_blob.BlobServiceClient",
        lambda **kwargs: mock_service_client,
    )

    io_obj = IOAzureBlobStorage(uuri=dummy_uuri)

    tags = io_obj.get_remote_tags()
    assert tags == {"key": "value"}


def test_upload_no_tags(monkeypatch, dummy_uuri, tmp_path):
    from unittest.mock import MagicMock

    mock_blob_client = MagicMock()
    mock_blob_client.upload_blob.return_value = None

    mock_container_client = MagicMock()
    mock_container_client.get_blob_client.return_value = mock_blob_client

    mock_service_client = MagicMock()
    mock_service_client.get_container_client.return_value = mock_container_client

    monkeypatch.setattr(
        "urgap.ufile.io.azure_blob.BlobServiceClient",
        lambda **kwargs: mock_service_client,
    )

    scratch_file = tmp_path / "scratch.txt"
    scratch_file.write_text("hello world")

    io_obj = IOAzureBlobStorage(uuri=dummy_uuri)

    monkeypatch.setattr(
        type(io_obj), "scratch_path", property(lambda self: scratch_file)
    )

    io_obj.upload(tags=None)
    mock_blob_client.upload_blob.assert_called_once()


def test_upload_large_tags(monkeypatch, dummy_uuri, tmp_path):
    from unittest.mock import MagicMock

    mock_blob_client = MagicMock()
    mock_blob_client.upload_blob.return_value = None

    mock_container_client = MagicMock()
    mock_container_client.get_blob_client.return_value = mock_blob_client

    mock_service_client = MagicMock()
    mock_service_client.get_container_client.return_value = mock_container_client

    monkeypatch.setattr(
        "urgap.ufile.io.azure_blob.BlobServiceClient",
        lambda **kwargs: mock_service_client,
    )

    scratch_file = tmp_path / "scratch.txt"
    scratch_file.write_text("hello world")

    io_obj = IOAzureBlobStorage(uuri=dummy_uuri)

    monkeypatch.setattr(
        type(io_obj), "scratch_path", property(lambda self: scratch_file)
    )

    tags = {f"parent_key_{i}": "value" for i in range(150)}

    io_obj.upload(tags=tags)

    called_tags = mock_blob_client.upload_blob.call_args[1]["metadata"]
    assert called_tags.get("ParentsRemoved") == "Yes"


def test_remote_tag_path_property():
    mock_uuri = MagicMock()
    io_blob = IOAzureBlobStorage.__new__(IOAzureBlobStorage)
    io_blob.uuri = mock_uuri

    result = io_blob.remote_tag_path

    assert result is None


def test_get_remote_tags_existing_blob():
    io_blob = IOAzureBlobStorage.__new__(IOAzureBlobStorage)

    io_blob.blob = MagicMock()
    io_blob.remote_object_exists = MagicMock(return_value=True)

    io_blob.blob.get_blob_properties.return_value = {
        "metadata": {"key1": "value1", "key2": "value2"}
    }

    tags = io_blob.get_remote_tags()

    assert tags == {"key1": "value1", "key2": "value2"}
    io_blob.blob.get_blob_properties.assert_called_once()


def test_get_remote_tags_nonexistent_blob():
    io_blob = IOAzureBlobStorage.__new__(IOAzureBlobStorage)

    io_blob.remote_object_exists = MagicMock(return_value=False)

    tags = io_blob.get_remote_tags()

    assert tags is None


def test_download_when_local_file_exists_and_hash_matches():
    io_blob = IOAzureBlobStorage.__new__(IOAzureBlobStorage)

    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True
    with patch.object(
        IOAzureBlobStorage, "scratch_path", new_callable=lambda: mock_path
    ):
        io_blob.blob = MagicMock()
        io_blob.blob.exists.return_value = True

        with patch("urgap.ucore.calculate_file_hash", return_value="fakehash"):
            with patch.object(
                io_blob, "get_remote_tags", return_value={"sha256": "fakehash"}
            ):
                io_blob.download()


def test_download_hash_matches():
    io_blob = IOAzureBlobStorage.__new__(IOAzureBlobStorage)

    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True
    with patch.object(
        IOAzureBlobStorage, "scratch_path", new_callable=lambda: mock_path
    ):
        io_blob.blob = MagicMock()
        io_blob.blob.exists.return_value = True

        with patch("urgap.ucore.calculate_file_hash", return_value="fakehash"):
            with patch.object(
                io_blob, "get_remote_tags", return_value={"sha256": "fakehash"}
            ):
                io_blob.download()


def test_list_container_items_with_and_without_pattern():
    io_blob = IOAzureBlobStorage.__new__(IOAzureBlobStorage)

    io_blob.container = MagicMock()
    io_blob.add_storage_uri_to_container_items = lambda x: x
    io_blob.container.list_blob_names.return_value = [
        "file1.txt",
        "file2.csv",
        "image.png",
        "data_file.txt",
    ]

    all_blobs = io_blob.list_container_items()
    assert all_blobs == ["file1.txt", "file2.csv", "image.png", "data_file.txt"]

    txt_blobs = io_blob.list_container_items(pattern=r"\.txt$")
    assert txt_blobs == ["file1.txt", "data_file.txt"]

    none_blobs = io_blob.list_container_items(pattern=r"\.pdf$")
    assert none_blobs == []
