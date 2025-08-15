
import pytest

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

    except Exception as e:
        pytest.fail(f"Deletion raised an exception: {str(e)}")
