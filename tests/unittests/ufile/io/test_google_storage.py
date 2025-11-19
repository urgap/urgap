import re

from unittest.mock import MagicMock, patch

import pytest

from urgap.ufile.io.google_storage import IOGoogleCloudStorage


@pytest.fixture
def mock_io_gcs(tmp_path):
    mock_uuri = MagicMock()
    mock_uuri.netloc = "mock-project"
    mock_uuri.get_container_name.return_value = "mock-bucket"
    mock_uuri.get_object_name.return_value = "mock-object"

    mock_kwargs = {"uuri": mock_uuri, "scratch_path": tmp_path / "mock_file"}

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
    io_gcs.blob.upload_from_filename = MagicMock()
    io_gcs.upload(tags={"key": "value"})
    io_gcs.blob.upload_from_filename.assert_called_once_with(
        filename=io_gcs.scratch_path,
    )


def test_remote_paths_are_none(mock_io_gcs):
    assert mock_io_gcs.remote_path is None
    assert mock_io_gcs.remote_tag_path is None


def test_get_remote_tags_returns_metadata_or_none(mock_io_gcs):
    mock_blob = MagicMock()
    mock_blob.metadata = {"key": "value"}
    mock_io_gcs.bucket.get_blob.return_value = mock_blob
    assert mock_io_gcs.get_remote_tags() == {"key": "value"}

    mock_io_gcs.bucket.get_blob.return_value = None
    assert mock_io_gcs.get_remote_tags() is None


def test_upload_skips_when_no_tags(monkeypatch, caplog, mock_io_gcs):
    caplog.set_level("WARNING")
    mock_io_gcs.upload(tags=None)
    assert "No tags provided, skipping upload." in caplog.text


def test_remote_object_exists(mock_io_gcs):
    mock_io_gcs.blob.exists.return_value = True
    assert mock_io_gcs.remote_object_exists() is True
    mock_io_gcs.blob.exists.return_value = False
    assert mock_io_gcs.remote_object_exists() is False


class MockBlob:
    def __init__(self, name):
        self.name = name


class MockStorage:
    def __init__(self, client, uuri):
        self.client = client
        self.uuri = uuri

    def add_storage_uri_to_container_items(self, blobs, pattern=None):
        container_objects = [blob.name for blob in blobs]
        if pattern is not None:
            container_objects = [
                name for name in container_objects if re.search(pattern, name)
            ]
        return container_objects

    def list_container_objects(self, pattern=None):
        blobs = self.client.list_blobs(bucket_or_name=self.uuri.get_container_name())
        return self.add_storage_uri_to_container_items(blobs, pattern)


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


    mock_uuri = MagicMock()
    mock_uuri.netloc = "test-project"
    mock_uuri.get_container_name.return_value = "test-bucket"
    mock_uuri.get_object_name.return_value = "test-object"

    # Mock dict password (service account JSON)

    mock_kwargs = {"uuri": mock_uuri, "scratch_path": tmp_path / "test_file"}

    with (
        patch(
            "urgap.ufile.io.google_storage.service_account.Credentials",
        ) as mock_creds_class,
        patch("urgap.ufile.io.google_storage.storage.Client") as mock_client_class,
    ):
        mock_credentials = MagicMock()
        mock_creds_class.from_service_account_info.return_value = mock_credentials
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        io_gcs = IOGoogleCloudStorage(**mock_kwargs)

        # Verify service account credentials were created from dict
        mock_creds_class.from_service_account_info.assert_called_once_with(
        )

        # Verify client was created with credentials and project
        mock_client_class.assert_called_once_with(
            credentials=mock_credentials,
            project="test-project",
        )


def test_init_with_string_password_creates_client_without_credentials(tmp_path):
    """Test that non-dict password creates default client."""
    mock_uuri = MagicMock()
    mock_uuri.netloc = "test-project"
    mock_uuri.get_container_name.return_value = "test-bucket"
    mock_uuri.get_object_name.return_value = "test-object"

    # Mock string password (or None)

    mock_kwargs = {"uuri": mock_uuri, "scratch_path": tmp_path / "test_file"}

    with (
        patch(
            "urgap.ufile.io.google_storage.service_account.Credentials",
        ) as mock_creds_class,
        patch("urgap.ufile.io.google_storage.storage.Client") as mock_client_class,
    ):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        io_gcs = IOGoogleCloudStorage(**mock_kwargs)

        # Verify service account credentials were NOT created
        mock_creds_class.from_service_account_info.assert_not_called()

        # Verify client was created with only project (no credentials)