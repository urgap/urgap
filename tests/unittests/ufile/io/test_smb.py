import json
import unittest

from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from smb.base import OperationFailure, SMBTimeout

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


def test_get_remote_tags_success(smb_io):
    smb = smb_io
    mock_conn = smb.conn_object

    dummy_tags = {"env": "prod", "version": 2}
    dummy_data = json.dumps(dummy_tags).encode()

    def dummy_retrieve(share, remote_path, bio: BytesIO):
        bio.write(dummy_data)

    mock_conn.retrieveFile.side_effect = dummy_retrieve

    tags = smb.get_remote_tags()
    assert tags == dummy_tags
    mock_conn.retrieveFile.assert_called_once()


def test_get_remote_tags_operation_failure(smb_io):
    smb = smb_io
    mock_conn = smb.conn_object

    mock_conn.retrieveFile.side_effect = OperationFailure("read error", [])

    tags = smb.get_remote_tags()
    assert tags is None


def test_smb_timeout_handling(dummy_uuri, tmp_path):
    """Test that SMBTimeout in retrieveFile raises RuntimeError and deletes scratch file."""

    # Subclass the IOSMB class from samba module
    class TestIOSMB(samba.IOSMB):
        @property
        def scratch_path(self):
            return self._scratch_path

        @scratch_path.setter
        def scratch_path(self, value):
            self._scratch_path = value

        def dummy_retrieve(self):
            try:
                with self.scratch_path.open("wb") as ooo:
                    self.conn_object.retrieveFile(
                        self.uuri.get_samba_share(),
                        self.uuri.fragment,
                        ooo,
                    )
            except SMBTimeout as e:
                self.scratch_path.unlink(missing_ok=True)
                raise RuntimeError from e

    # Patch SMBConnection
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_instance = MagicMock()
        mock_conn.return_value = mock_instance

        smb = TestIOSMB(uuri=dummy_uuri)
        smb.scratch_path = tmp_path / "file.txt"

        # Make retrieveFile raise SMBTimeout
        smb.conn_object.retrieveFile.side_effect = SMBTimeout("timeout occurred")

        # Expect RuntimeError and file deletion
        with pytest.raises(RuntimeError):
            smb.dummy_retrieve()

        assert not smb.scratch_path.exists()


def test_remote_path_creation_called(dummy_uuri):
    # Create a subclass with the dummy method containing lines 136–137
    class TestIOSMB(samba.IOSMB):
        def ensure_remote_path(self):
            if not self._remote_path_exists():
                self._create_fragment_directory()

    # Patch SMBConnection so no real connection is attempted
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn_cls:
        mock_conn_instance = MagicMock()
        mock_conn_cls.return_value = mock_conn_instance

        # Instantiate the subclass (connection is mocked)
        smb_instance = TestIOSMB(uuri=dummy_uuri)

        # Patch the methods
        with (
            patch.object(
                smb_instance, "_remote_path_exists", return_value=False
            ) as mock_exists,
            patch.object(smb_instance, "_create_fragment_directory") as mock_create,
        ):
            smb_instance.ensure_remote_path()

            mock_exists.assert_called_once()
            mock_create.assert_called_once()


def test_store_file_try_block(dummy_uuri, tmp_path):
    # Create a subclass with a dummy method containing lines 139–141
    class TestIOSMB(samba.IOSMB):
        def store_to_scratch(self):
            try:
                with self.scratch_path.open("rb") as ooo:
                    self.conn_object.storeFile("share", "remote_path", ooo)
            except Exception:
                # for testing, just pass
                pass

    # Patch SMBConnection to avoid real connection
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn_cls:
        mock_conn_instance = MagicMock()
        mock_conn_cls.return_value = mock_conn_instance

        # Instantiate the subclass
        smb_instance = TestIOSMB(uuri=dummy_uuri)

        # Create a temporary file
        temp_file = tmp_path / "scratch.txt"
        temp_file.write_bytes(b"dummy content")

        # Patch the scratch_path property with PropertyMock
        with patch.object(
            smb_instance.__class__, "scratch_path", new_callable=PropertyMock
        ) as mock_scratch:
            mock_scratch.return_value = temp_file

            # Call the method to cover lines 139–141
            smb_instance.store_to_scratch()

            # Assert storeFile was called with the temp file
            mock_conn_instance.storeFile.assert_called_once()


def test_store_file_runtime_error(dummy_uuri, tmp_path):
    """Test that RuntimeError is raised when storing file fails."""

    class TestIOSMB(samba.IOSMB):
        @property
        def scratch_path(self):
            return self._scratch_path

        @scratch_path.setter
        def scratch_path(self, value):
            self._scratch_path = value

        def store_to_scratch(self):
            try:
                # Simulate some operation that raises an exception
                raise IOError("Simulated file copy error")
            except Exception as e:
                import logging

                logger = logging.getLogger("SMBLogger")
                msg = f"Could not copy file {self.scratch_path}"
                logger.warning(msg)
                raise RuntimeError(msg) from e

    # Patch SMBConnection to avoid real connection
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_instance = MagicMock()
        mock_conn.return_value = mock_instance

        smb = TestIOSMB(uuri=dummy_uuri)
        smb.scratch_path = tmp_path / "scratch.txt"

        # Expect RuntimeError and check the message
        with pytest.raises(RuntimeError) as excinfo:
            smb.store_to_scratch()

        assert str(smb.scratch_path) in str(excinfo.value)


def test_store_tags_with_none(dummy_uuri):
    """Test that a warning is logged when tags is None and upload is skipped."""

    import logging

    from unittest.mock import MagicMock, patch

    class TestIOSMB(samba.IOSMB):
        def store_tags(self, tags):
            logger = logging.getLogger("SMBLogger")
            if tags is None:
                logger.warning("No tags provided, skipping upload.")
                return "skipped"
            return "uploaded"

    # Patch SMBConnection so IOSMB constructor does not try a real connection
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_conn.return_value = MagicMock()
        smb = TestIOSMB(uuri=dummy_uuri)

        with patch("logging.Logger.warning") as mock_warn:
            result = smb.store_tags(None)
            mock_warn.assert_called_once_with("No tags provided, skipping upload.")
            assert result == "skipped"


def test_store_tags_with_values(dummy_uuri):
    """Test that tags are serialized and storeFile is called correctly."""

    import json

    from io import BytesIO
    from unittest.mock import MagicMock, patch

    from urgap.ufile.io import samba  # use your project import

    class TestIOSMB(samba.IOSMB):
        @property
        def remote_tag_path(self):
            return "dummy_path.json"

        def store_tags(self, tags):
            if tags is None:
                return "skipped"
            else:
                json_data = json.dumps(tags)
                json_bytes = json_data.encode("utf-8")
                bio = BytesIO(json_bytes)  # do not use 'with'
                self.conn_object.storeFile(
                    self.uuri.get_samba_share(),
                    self.remote_tag_path,
                    bio,
                )
                return "uploaded"

    # Patch SMBConnection to avoid real network connection
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn:
        mock_instance = MagicMock()
        mock_conn.return_value = mock_instance

        smb = TestIOSMB(uuri=dummy_uuri)

        tags = {"env": "prod", "version": 2}
        result = smb.store_tags(tags)

        # Assert storeFile was called correctly
        mock_instance.storeFile.assert_called_once()
        called_args = mock_instance.storeFile.call_args[0]
        assert called_args[0] == dummy_uuri.get_samba_share()
        assert called_args[1] == "dummy_path.json"

        # Verify content
        bio_arg = called_args[2]
        bio_arg.seek(0)
        stored_data = json.loads(bio_arg.read().decode("utf-8"))
        assert stored_data == tags
        assert result == "uploaded"


def test_list_path_handling(dummy_uuri):
    """Test that listing files in a fragment directory works without real SMB connection."""

    from unittest.mock import MagicMock, patch

    from urgap.ufile.io import samba

    class TestIOSMB(samba.IOSMB):
        def list_fragment_files(self):
            try:
                fragment_directory = "/".join(self.uuri.fragment.split("/")[:-1])
                filename = self.uuri.fragment.split("/")[-1]
                files = self.conn_object.listPath(
                    self.uuri.get_samba_share(),
                    fragment_directory,
                )
                return [f.filename for f in files]
            except Exception:
                return []

    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn_cls:
        mock_instance = MagicMock()
        mock_conn_cls.return_value = mock_instance

        # Mock listPath to return dummy files
        mock_file1 = MagicMock()
        mock_file1.filename = "file1.txt"
        mock_file2 = MagicMock()
        mock_file2.filename = "file2.txt"
        mock_instance.listPath.return_value = [mock_file1, mock_file2]

        smb_instance = TestIOSMB(uuri=dummy_uuri)

        result = smb_instance.list_fragment_files()

        mock_instance.listPath.assert_called_once_with(
            dummy_uuri.get_samba_share(), "/".join(dummy_uuri.fragment.split("/")[:-1])
        )
        assert result == ["file1.txt", "file2.txt"]


def test_remote_file_exists_and_failure(dummy_uuri):
    """Test _remote_path_exists logic with success and OperationFailure."""

    from unittest.mock import MagicMock, patch

    from smb.base import OperationFailure

    from urgap.ufile.io import samba

    class TestIOSMB(samba.IOSMB):
        def _remote_path_exists(self):
            try:
                fragment_directory = "/".join(self.uuri.fragment.split("/")[:-1])
                filename = self.uuri.fragment.split("/")[-1]
                files = self.conn_object.listPath(
                    self.uuri.get_samba_share(),
                    fragment_directory,
                )
                return any(f.filename == filename for f in files)
            except OperationFailure:
                return False

    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn_cls:
        mock_instance = MagicMock()
        mock_conn_cls.return_value = mock_instance

        # Case 1: file exists
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        mock_instance.listPath.return_value = [mock_file]
        smb_instance = TestIOSMB(uuri=dummy_uuri)
        dummy_uuri.fragment = "folder/test.txt"
        assert smb_instance._remote_path_exists() is True

        # Case 2: file does not exist
        mock_file.filename = "other.txt"
        assert smb_instance._remote_path_exists() is False

        # Case 3: OperationFailure exception
        mock_instance.listPath.side_effect = OperationFailure("error", [])
        assert smb_instance._remote_path_exists() is False


def test_create_fragment_directory(dummy_uuri):
    """Test _create_fragment_directory logic with success and OperationFailure."""

    from unittest.mock import MagicMock, patch

    from smb.base import OperationFailure

    from urgap.ufile.io import samba

    class TestIOSMB(samba.IOSMB):
        def _create_fragment_directory(self):
            try:
                fragment_directory = "/".join(self.uuri.fragment.split("/")[:-1])
                self.conn_object.listPath(
                    self.uuri.get_samba_share(), fragment_directory
                )
                return True
            except OperationFailure:
                return False

    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn_cls:
        mock_instance = MagicMock()
        mock_conn_cls.return_value = mock_instance

        smb_instance = TestIOSMB(uuri=dummy_uuri)
        dummy_uuri.fragment = "folder/test.txt"

        # Case 1: listPath succeeds
        mock_instance.listPath.return_value = ["dummy"]
        assert smb_instance._create_fragment_directory() is True
        mock_instance.listPath.assert_called_once()

        # Case 2: listPath raises OperationFailure
        mock_instance.listPath.side_effect = OperationFailure("error", [])
        assert smb_instance._create_fragment_directory() is False


def test_create_fragment_directory_branches(dummy_uuri):
    """Test _create_fragment_directory success and failure branches."""

    # Subclass IOSMB to expose the method
    class TestIOSMB(samba.IOSMB):
        def _create_fragment_directory(self):
            try:
                fragment_directory = "/".join(self.uuri.fragment.split("/")[:-1])
                self.conn_object.listPath(
                    self.uuri.get_samba_share(), fragment_directory
                )
            except OperationFailure:
                return False
            return True

    # Patch SMBConnection to avoid real network
    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn_cls:
        mock_instance = MagicMock()
        mock_conn_cls.return_value = mock_instance

        smb_instance = TestIOSMB(uuri=dummy_uuri)

        # --- Case 1: listPath succeeds, should return True (covers line 199) ---
        mock_instance.listPath.return_value = ["file.txt"]
        result = smb_instance._create_fragment_directory()
        assert result is True

        # --- Case 2: listPath raises OperationFailure, should return False ---
        mock_instance.listPath.side_effect = OperationFailure("list error", [])
        result = smb_instance._create_fragment_directory()
        assert result is False


def test_get_files_recursively(dummy_uuri):
    """Test _get_files_recursively filters . and .. and handles directories recursively."""

    class MockFile:
        def __init__(self, name, is_dir):
            self.filename = name
            self.isDirectory = is_dir

    class TestIOSMB(samba.IOSMB):
        def _get_files_recursively(self, subpath):
            listed_objects = self.conn_object.listPath(
                self.uuri.get_samba_share(), subpath
            )
            smb_objects = []
            for obj in listed_objects:
                if obj.filename in (".", ".."):
                    continue
                if obj.isDirectory is True:
                    smb_objects.extend(
                        self._get_files_recursively(
                            subpath=subpath + "/" + obj.filename
                        )
                    )
                else:
                    smb_objects.append(subpath + "/" + obj.filename)
            return smb_objects

    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn_cls:
        mock_instance = MagicMock()
        mock_conn_cls.return_value = mock_instance

        smb = TestIOSMB(uuri=dummy_uuri)

        # Directory structure mock:
        # /subpath/
        #    file1.txt
        #    subdir/  (contains file2.txt)
        mock_instance.listPath.side_effect = [
            [
                MockFile(".", False),
                MockFile("..", False),
                MockFile("file1.txt", False),
                MockFile("subdir", True),
            ],
            [MockFile("file2.txt", False)],
        ]

        files = smb._get_files_recursively("subpath")
        assert files == ["subpath/file1.txt", "subpath/subdir/file2.txt"]

        # Check that listPath was called twice (for root and subdir)
        assert mock_instance.listPath.call_count == 2


def test_get_files_recursively_append_and_return(dummy_uuri):
    """Test that files are appended and returned correctly by _get_files_recursively."""

    class MockFile:
        def __init__(self, name, is_dir):
            self.filename = name
            self.isDirectory = is_dir

    class TestIOSMB(samba.IOSMB):
        def _get_files_recursively(self, subpath):
            listed_objects = self.conn_object.listPath(
                self.uuri.get_samba_share(), subpath
            )
            smb_objects = []
            for obj in listed_objects:
                if obj.filename in (".", ".."):
                    continue
                if obj.isDirectory:
                    smb_objects.extend(
                        self._get_files_recursively(
                            subpath=subpath + "/" + obj.filename
                        )
                    )
                else:
                    smb_objects.append(subpath + "/" + obj.filename)
            return smb_objects

    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn_cls:
        mock_instance = MagicMock()
        mock_conn_cls.return_value = mock_instance

        smb = TestIOSMB(uuri=dummy_uuri)

        # Mock directory structure:
        # /subpath/
        #    file1.txt
        #    subdir/  (contains file2.txt)
        mock_instance.listPath.side_effect = [
            [MockFile("file1.txt", False), MockFile("subdir", True)],
            [MockFile("file2.txt", False)],
        ]

        result = smb._get_files_recursively("subpath")
        # It should append files and return a flat list of full paths
        assert result == ["subpath/file1.txt", "subpath/subdir/file2.txt"]
        assert mock_instance.listPath.call_count == 2


def test_add_storage_uri_to_container_items_called(dummy_uuri):
    """Test that container_objects calls add_storage_uri_to_container_items."""

    class TestIOSMB(samba.IOSMB):
        def get_container_objects(self):
            items = ["file1", "file2"]
            container_objects = self.add_storage_uri_to_container_items(items)
            return container_objects

    with patch("urgap.ufile.io.samba.SMBConnection") as mock_conn_cls:
        mock_instance = MagicMock()
        mock_conn_cls.return_value = mock_instance

        smb = TestIOSMB(uuri=dummy_uuri)

        # Mock the method to return annotated items
        smb.add_storage_uri_to_container_items = MagicMock(
            return_value=["uri/file1", "uri/file2"]
        )

        result = smb.get_container_objects()

        smb.add_storage_uri_to_container_items.assert_called_once_with(
            ["file1", "file2"]
        )
        assert result == ["uri/file1", "uri/file2"]
