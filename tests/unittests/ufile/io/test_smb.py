from io import BytesIO
from pathlib import Path

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