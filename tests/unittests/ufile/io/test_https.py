import urllib.error

from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

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


import urllib.error

from pathlib import Path
from unittest.mock import MagicMock, patch


def test_iohttps_download_urlerror():
    class DummyUURI:
        def get_https_remote_path(self):
            return "https://example.com/file.txt"

    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = DummyUURI()

    def scratch_path_prop(self):
        return Path("/tmp/scratch_file.txt")

    with patch.object(type(iohttps), "scratch_path", new=property(scratch_path_prop)):
        with patch(
            "urllib.request.urlretrieve", side_effect=urllib.error.URLError("fail")
        ):
            with patch("urgap.ufile.io.https.logger") as mock_logger:
                iohttps.download()
                mock_logger.warning.assert_called()


import pytest

from urgap.ufile.io.https import IOHTTPS


def test_iohttps_upload_not_implemented():
    class DummyUURI:
        def get_https_remote_path(self):
            return "https://example.com/file.txt"

    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = DummyUURI()

    import logging

    from unittest.mock import patch

    with patch("urgap.ufile.io.https.logger") as mock_logger:
        with pytest.raises(NotImplementedError) as exc_info:
            iohttps.upload(tags=None)

        mock_logger.warning.assert_called_with("No tags provided, skipping upload.")

        assert str(exc_info.value) == "Cannot upload via https!"


from pathlib import Path
from unittest.mock import PropertyMock, patch
from urllib.error import HTTPError

import pytest

from urgap.ufile.io.https import IOHTTPS


def test_iohttps_remote_object_exists_true():
    class DummyUURI:
        def get_https_remote_path(self):
            return "https://example.com/file.txt"

    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = DummyUURI()

    with patch.object(
        type(iohttps), "scratch_path", new_callable=PropertyMock
    ) as mock_scratch:
        mock_scratch.return_value = Path("/tmp/scratch_file.txt")
        with patch("urllib.request.urlretrieve") as mock_urlretrieve:
            exists = iohttps.remote_object_exists()
            mock_urlretrieve.assert_called_once_with(
                "https://example.com/file.txt", filename=Path("/tmp/scratch_file.txt")
            )
            assert exists is True


def test_iohttps_remote_object_exists_false():
    class DummyUURI:
        def get_https_remote_path(self):
            return "https://example.com/file.txt"

    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = DummyUURI()

    with patch.object(
        type(iohttps), "scratch_path", new_callable=PropertyMock
    ) as mock_scratch:
        mock_scratch.return_value = Path("/tmp/scratch_file.txt")
        with patch(
            "urllib.request.urlretrieve",
            side_effect=HTTPError(url="", code=404, msg="", hdrs=None, fp=None),
        ):
            exists = iohttps.remote_object_exists()
            assert exists is False


def test_remote_object_exists_true():
    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = type(
        "DummyUURI",
        (),
        {"get_https_remote_path": lambda self: "https://example.com/file.txt"},
    )()

    with patch.object(
        type(iohttps), "scratch_path", new_callable=PropertyMock
    ) as mock_scratch:
        mock_scratch.return_value = Path("/tmp/scratch_file.txt")
        with patch("urllib.request.urlretrieve") as mock_urlretrieve:
            exists = iohttps.remote_object_exists()
            assert exists is True


def test_remote_object_exists_false():
    iohttps = IOHTTPS.__new__(IOHTTPS)
    iohttps.uuri = type(
        "DummyUURI",
        (),
        {"get_https_remote_path": lambda self: "https://example.com/file.txt"},
    )()

    with patch.object(
        type(iohttps), "scratch_path", new_callable=PropertyMock
    ) as mock_scratch:
        mock_scratch.return_value = Path("/tmp/scratch_file.txt")
        with patch(
            "urllib.request.urlretrieve",
            side_effect=HTTPError(url="", code=404, msg="", hdrs=None, fp=None),
        ):
            exists = iohttps.remote_object_exists()
            assert exists is False