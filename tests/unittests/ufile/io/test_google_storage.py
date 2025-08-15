import re


import pytest

from urgap.ufile.io.google_storage import IOGoogleCloudStorage


@pytest.fixture
    mock_uuri = MagicMock()
    mock_uuri.netloc = "mock-project"
    mock_uuri.get_container_name.return_value = "mock-bucket"
    mock_uuri.get_object_name.return_value = "mock-object"


    with patch("urgap.ufile.io.google_storage.storage.Client") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_bucket = mock_client.bucket.return_value
        mock_blob = mock_bucket.blob.return_value

        io_gcs = IOGoogleCloudStorage(**mock_kwargs)
        io_gcs.client = mock_client
        io_gcs.bucket = mock_bucket
        io_gcs.blob = mock_blob

        yield io_gcs


def test_upload_calls_blob_upload_from_filename(mock_io_gcs):
    io_gcs = mock_io_gcs




    mock_blob = MagicMock()
    mock_blob.metadata = {"key": "value"}



def test_upload_skips_when_no_tags(monkeypatch, caplog, mock_io_gcs):
    caplog.set_level("WARNING")
    assert "No tags provided, skipping upload." in caplog.text




class MockBlob:
    def __init__(self, name):
        self.name = name


class MockStorage:
    def __init__(self, client, uuri):
        self.client = client
        self.uuri = uuri

    def add_storage_uri_to_container_items(self, blobs, pattern=None):
        if pattern is not None:
            container_objects = [
            ]
        return container_objects

    def list_container_objects(self, pattern=None):


@pytest.fixture
def mock_storage():
    client = MagicMock()
    uuri = MagicMock()
    uuri.get_container_name.return_value = "my_bucket"
    client.list_blobs.return_value = [
        MockBlob("file1.txt"),
        MockBlob("file2.csv"),
        MockBlob("image.png"),
    ]
    return MockStorage(client, uuri)


def test_list_container_objects_no_pattern(mock_storage):
    result = mock_storage.list_container_objects()
    assert result == ["file1.txt", "file2.csv", "image.png"]


def test_list_container_objects_with_pattern(mock_storage):
    result = mock_storage.list_container_objects(pattern=r"\.txt$")
    assert result == ["file1.txt"]