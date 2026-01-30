from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from urgap.ufile.io.https import IOHTTPS


def test_iohttps_get_object():
    class DummyUURI:
        def get_https_remote_path(self):
            return "https://example.com/file.txt"

    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = DummyUURI()

    obj = iohttps.get_object()
    assert obj == "https://example.com/file.txt"


def test_iohttps_download_success():
    class DummyUURI:
        def get_https_remote_path(self):
            return "https://example.com/file.txt"

    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = DummyUURI()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"file content"

    with patch.object(
        type(iohttps), "scratch_path", new_callable=PropertyMock
    ) as mock_scratch:
        mock_file = MagicMock()
        mock_scratch.return_value.open.return_value.__enter__.return_value = mock_file
        with patch("urgap.ufile.io.https.requests.get", return_value=mock_response):
            iohttps.download()
            mock_scratch.return_value.open.assert_called_once_with("wb")
            mock_file.write.assert_called_once_with(b"file content")


def test_iohttps_download_failure():
    class DummyUURI:
        def get_https_remote_path(self):
            return "https://example.com/file.txt"

    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = DummyUURI()

    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch.object(
        type(iohttps), "scratch_path", new_callable=PropertyMock
    ) as mock_scratch:
        with patch("urgap.ufile.io.https.requests.get", return_value=mock_response):
            iohttps.download()
            mock_scratch.return_value.unlink.assert_called_once()


def test_iohttps_upload_not_implemented():
    class DummyUURI:
        def get_https_remote_path(self):
            return "https://example.com/file.txt"

    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = DummyUURI()

    with patch("urgap.ufile.io.https.logger") as mock_logger:
        with pytest.raises(NotImplementedError) as exc_info:
            iohttps.upload(tags=None)

        mock_logger.warning.assert_called_with("No tags provided, skipping upload.")

        assert str(exc_info.value) == "Cannot upload via https!"


def test_iohttps_remote_object_exists_true():
    class DummyUURI:
        def get_https_remote_path(self):
            return "https://example.com/file.txt"

    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = DummyUURI()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"file content"

    with patch.object(
        type(iohttps), "scratch_path", new_callable=PropertyMock
    ) as mock_scratch:
        mock_file = MagicMock()
        mock_scratch.return_value.open.return_value.__enter__.return_value = mock_file
        with patch("urgap.ufile.io.https.requests.get", return_value=mock_response):
            exists = iohttps.remote_object_exists()
            assert exists is True


def test_iohttps_remote_object_exists_false():
    class DummyUURI:
        def get_https_remote_path(self):
            return "https://example.com/file.txt"

    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = DummyUURI()

    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("urgap.ufile.io.https.requests.get", return_value=mock_response):
        exists = iohttps.remote_object_exists()
        assert exists is False
