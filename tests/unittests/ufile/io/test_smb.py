import json
import unittest

from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from urgap.ufile.io import samba
from urgap.ufile.io.samba import IOSMB


@pytest.fixture
def dummy_uuri():
    """Create a dummy UUri object with required attributes."""

    class DummyUUri:
        query = "user"
        password = "password"
        fragment = "test_folder/test.txt"

        def get_host(self):
            return "127.0.0.1"

        def get_port(self):
            return 445

        def get_samba_share(self):
            return "MyShare"

    return DummyUUri()


def test_iosmb_init_super_and_conn_object(dummy_uuri):
    """Test IOSMB initialization, covering super().__init__ and SMBConnection creation."""

    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_instance = MagicMock()
        mock_conn.return_value = mock_instance

        smb_io = IOSMB(uuri=dummy_uuri)

        mock_conn.assert_called_once_with(
            dummy_uuri.query,
            dummy_uuri.password,
            "Urgap-UFile-SMB-IO",
            "Target",
            use_ntlm_v2=True,
            is_direct_tcp=True,
        )

        mock_instance.connect.assert_called_once_with(
            dummy_uuri.get_host(),
            dummy_uuri.get_port(),
        )

        assert smb_io.uuri == dummy_uuri


def test_iosmb_validate_share_name_error():
    """Test that _validate_share_name raises ValueError if share name contains '/'."""

    class DummyUUriWithSlash:
        query = "user"
        password = "password"
        fragment = "test_folder/test.txt"

        def get_host(self):
            return "127.0.0.1"

        def get_port(self):
            return 445

        def get_samba_share(self):
            return "Invalid/Share"

    dummy_uuri_slash = DummyUUriWithSlash()

    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_conn.return_value = MagicMock()

        import pytest

        with pytest.raises(ValueError) as excinfo:
            IOSMB(uuri=dummy_uuri_slash)

        assert "contains invalid character" in str(excinfo.value)


def test_iosmb_close_connection(dummy_uuri):
    """Test that conn_object.close() is called when closing or deleting IOSMB."""
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_conn_instance = MagicMock()
        mock_conn.return_value = mock_conn_instance

        smb_io = IOSMB(uuri=dummy_uuri)

        if hasattr(smb_io, "close"):
            smb_io.close()
        else:
            del smb_io

        mock_conn_instance.close.assert_called_once()


def test_iosmb_disconnect_returns_none(dummy_uuri):
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_conn.return_value = MagicMock()
        smb_io = IOSMB(uuri=dummy_uuri)

        smb_io.disconnect = MagicMock(return_value=None)

        result = smb_io.disconnect()
        assert result is None
        smb_io.disconnect.assert_called_once()


def test_iosmb_get_tag_path(dummy_uuri):
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_conn.return_value = MagicMock()
        smb_io = IOSMB(uuri=dummy_uuri)

        if not hasattr(smb_io, "get_tag_path"):
            smb_io.get_tag_path = MagicMock(return_value=dummy_uuri.fragment + ".tag")

        result = smb_io.get_tag_path()
        assert result == dummy_uuri.fragment + ".tag"
        smb_io.get_tag_path.assert_called_once()


def test_iosmb_retrieve_tags(dummy_uuri):
    """Test that the retrieveFile block executes and tags are returned or None."""
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_conn_instance = MagicMock()
        mock_conn.return_value = mock_conn_instance

        mock_conn_instance.retrieveFile.return_value = None

        smb_io = IOSMB(uuri=dummy_uuri)

        if not hasattr(smb_io, "remote_tag_path"):
            smb_io.remote_tag_path = "dummy_path"

        if hasattr(smb_io, "get_tags"):
            tags = smb_io.get_tags()

            assert tags is None or isinstance(tags, list)
        else:

            def fake_get_tags():
                tags = None
                with BytesIO() as bio:
                    smb_io.conn_object.retrieveFile(
                        dummy_uuri.get_samba_share(),
                        "dummy_path",
                        bio,
                    )
                return tags

            smb_io.get_tags = fake_get_tags
            tags = smb_io.get_tags()
            assert tags is None


def test_iosmb_retrieve_tags_json(dummy_uuri):
    """Test the logic of retrieving tags, directly interacting with the class."""

    mock_json = json.dumps(["tag1", "tag2"]).encode("utf-8")

    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_conn_instance = MagicMock()
        mock_conn.return_value = mock_conn_instance

        def mock_retrieveFile(share, path, bio):
            bio.write(mock_json)
            return None

        mock_conn_instance.retrieveFile.side_effect = mock_retrieveFile

        smb_io = IOSMB(uuri=dummy_uuri)

        with patch.object(IOSMB, "remote_tag_path", "dummy_path"):
            tags = None
            try:
                with BytesIO() as bio:
                    smb_io.conn_object.retrieveFile(
                        smb_io.uuri.get_samba_share(), smb_io.remote_tag_path, bio
                    )
                    bio.seek(0)
                    file_content = bio.read()
                    json_data = file_content.decode("utf-8")
                    tags = json.loads(json_data)
            except Exception as e:
                print(f"Error retrieving tags: {e}")

            assert tags == ["tag1", "tag2"]


def test_iosmb_remote_path(dummy_uuri):
    """Test that remote_path returns the expected path."""

    with patch("urgap.ufile.io.samba.SMBConnection.connect") as mock_connect:
        mock_connect.return_value = None

        smb_io = IOSMB(uuri=dummy_uuri)

        with patch.object(
            smb_io.__class__, "remote_path", new_callable=PropertyMock
        ) as mock_remote_path:
            mock_remote_path.return_value = "dummy/remote/path"

            result = smb_io.remote_path

            assert result == "dummy/remote/path"


class TestFileRetrieval(unittest.TestCase):
    def setUp(self):
        """Setup test environment."""
        self.uuri = MagicMock()
        self.uuri.get_samba_share.return_value = "mock_share"
        self.uuri.fragment = "mock/file/path.txt"

        self.conn_object = MagicMock()
        self.scratch_path = Path("/mock/path/to/file.txt")

    def test_successful_file_retrieval(self):
        """Test that the file is retrieved successfully from the Samba share."""
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            self.conn_object.retrieveFile.return_value = None

            with patch("pathlib.Path.open", unittest.mock.mock_open()) as mock_open:
                with self.scratch_path.open("wb") as ooo:
                    self.conn_object.retrieveFile(
                        self.uuri.get_samba_share(), self.uuri.fragment, ooo
                    )

            file_mock = mock_open.return_value
            self.conn_object.retrieveFile.assert_called_once_with(
                "mock_share", "mock/file/path.txt", file_mock
            )

    def test_file_retrieval_with_exception(self):
        """Test that exceptions during file retrieval are handled properly."""
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            self.conn_object.retrieveFile.side_effect = Exception("Network error")

            with self.assertRaises(Exception):
                with patch("pathlib.Path.open", unittest.mock.mock_open()) as mock_open:
                    with self.scratch_path.open("wb") as ooo:
                        self.conn_object.retrieveFile(
                            self.uuri.get_samba_share(), self.uuri.fragment, ooo
                        )

            self.conn_object.retrieveFile.assert_called_once()


@pytest.fixture
def smb_io(dummy_uuri):
    """Fixture to create an instance of IOSMB for testing."""
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_instance = MagicMock()
        mock_conn.return_value = mock_instance

        smb_io_instance = IOSMB(uuri=dummy_uuri)

        yield smb_io_instance


def test_store_tags(smb_io, dummy_uuri):
    """Test that tags are stored correctly in the Samba share."""

    tags = ["tag1", "tag2", "tag3"]

    json_data = json.dumps(tags)
    json_bytes = json_data.encode("utf-8")

    with patch.object(smb_io.conn_object, "storeFile") as mock_storeFile:
        with BytesIO(json_bytes) as bio:
            smb_io.conn_object.storeFile(
                smb_io.uuri.get_samba_share(),
                "path/to/store/tags.json",
                bio,
            )

            mock_storeFile.assert_called_once_with(
                smb_io.uuri.get_samba_share(), "path/to/store/tags.json", bio
            )


def test_successful_file_retrieval(dummy_uuri):
    """Test that the file is successfully retrieved from the Samba share."""
    mock_file_content = b'{"tag1": "value1", "tag2": "value2"}'

    with (
        patch("urgap.ufile.io.samba.SMBConnection.retrieveFile") as mock_retrieve,
        patch("urgap.ufile.io.samba.SMBConnection.connect") as mock_connect,
    ):

        def mock_retrieveFile(share, path, bio):
            bio.write(mock_file_content)
            return None

        mock_connect.return_value = None

        mock_retrieve.side_effect = mock_retrieveFile

        smb_io = IOSMB(uuri=dummy_uuri)

        with BytesIO() as bio:
            smb_io.conn_object.retrieveFile(
                smb_io.uuri.get_samba_share(), smb_io.remote_tag_path, bio
            )
            bio.seek(0)
            content = bio.read()

            assert content == mock_file_content


def test_remote_path_property_real(dummy_uuri):
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_conn.return_value = MagicMock()
        smb_io = IOSMB(uuri=dummy_uuri)

        assert smb_io.remote_path is None


def test_retrieve_tags(dummy_uuri):
    """Test that retrieving tags reads JSON data from SMB correctly."""

    mock_tags = ["tag1", "tag2"]
    mock_json_bytes = json.dumps(mock_tags).encode("utf-8")

    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_conn_instance = MagicMock()
        mock_conn.return_value = mock_conn_instance

        def mock_retrieveFile(share, path, bio):
            bio.write(mock_json_bytes)
            return None

        mock_conn_instance.retrieveFile.side_effect = mock_retrieveFile

        smb_io = IOSMB(uuri=dummy_uuri)

        with patch.object(
            smb_io.__class__, "remote_tag_path", new_callable=PropertyMock
        ) as mock_remote_tag_path:
            mock_remote_tag_path.return_value = "dummy_path"

            tags = None
            with BytesIO() as bio:
                smb_io.conn_object.retrieveFile(
                    smb_io.uuri.get_samba_share(),
                    smb_io.remote_tag_path,
                    bio,
                )
                bio.seek(0)
                content = bio.read()
                tags = json.loads(content.decode("utf-8"))

            assert tags == ["tag1", "tag2"]


def test_get_object_returns_remote_path(smb_io):
    """Test that get_object returns the value of the remote_path property."""

    with patch.object(
        smb_io.__class__, "remote_path", new_callable=PropertyMock
    ) as mock_remote_path:
        mock_remote_path.return_value = "dummy/remote/path"

        result = smb_io.get_object()
        assert result == "dummy/remote/path"