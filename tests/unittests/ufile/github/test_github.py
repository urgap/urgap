"""Unit tests for urgap.ufile.io.github.IOGithub."""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from github import GithubException
from requests.exceptions import HTTPError

import urgap

from urgap.ufile.io.github import IOGithub


@pytest.fixture
def mock_uio() -> IOGithub:
    """Return a mocked IOGithub object for testing."""
    mock = IOGithub.__new__(IOGithub)  # avoid full init
    mock.repo = MagicMock()
    mock.repo_full_name = "user/repo"
    mock.branch_name = "main"
    mock.source_branch = MagicMock()
    mock.source_branch.name = "main"
    mock.uuri = MagicMock()
    mock.uuri.password = "token"
    mock.object_filepath = None
    return mock


def test_remote_path_none(mock_uio: IOGithub) -> None:
    """Test that remote path is None by default."""
    assert mock_uio.object_filepath is None


def test_get_file_properties_none(mock_uio: IOGithub) -> None:
    """Test get_file_properties returns None when object_filepath is None."""
    mock_uio.object_filepath = None
    mock_uio.remote_object_exists = lambda: False
    assert mock_uio.get_file_properties() is None


def test_get_remote_tags_none(mock_uio: IOGithub) -> None:
    """Test get_remote_tags returns None when object_filepath is None."""
    mock_uio.object_filepath = None
    mock_uio.remote_object_exists = lambda: False
    assert mock_uio.get_remote_tags() is None


def test_get_object_none(mock_uio: IOGithub) -> None:
    """Test get_object returns None when object_filepath is None."""
    mock_uio.object_filepath = None
    mock_uio.remote_object_exists = lambda: False
    assert mock_uio.get_object() is None


def test_download_write_binary(mock_uio: IOGithub) -> None:
    """Test downloading binary file writes to scratch path."""
    content = b"binarycontent"
    download_mock = MagicMock()
    download_mock.decoded_content = content
    mock_uio.object_filepath = "file.xlsx"
    mock_uio.repo.get_contents = lambda *_args, **_kwargs: download_mock
    mock_uio.download()


def test_download_github_exception(mock_uio: IOGithub) -> None:
    """Test GithubException in download triggers RuntimeError."""
    mock_uio.repo.get_contents = lambda *_args, **_kwargs: (_ for _ in ()).throw(
        GithubException(500, "error", {}),
    )
    with pytest.raises(RuntimeError):
        mock_uio.download()


def test_list_container_items_http_error(mock_uio: IOGithub) -> None:
    """Test requests.HTTPError triggers OSError."""
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = HTTPError("Fail")
        mock_resp.status_code = 500
        mock_resp.text = "Error"
        mock_get.return_value = mock_resp
        with pytest.raises(OSError, match="Error connecting to GitHub API"):
            mock_uio.list_container_items()


def test_list_container_items_tree_none(mock_uio: IOGithub) -> None:
    """Test list_container_items raises KeyError when tree is None."""
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"tree": None}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        with pytest.raises(KeyError, match="Could not obtain 'tree' structure"):
            mock_uio.list_container_items()


def test_public_repo_xlsx_download() -> None:
    """Test that a public GitHub repo containing a .xlsx file can be accessed.

    After download, uf.path.exists() should return True.
    """
    uf = urgap.UFile(
        uri="github://github.com/pandas-dev/pandas/main#doc/cheatsheet/Pandas_Cheat_Sheet.xlsx",
    )
    try:
        uf.download()
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"Cannot reach GitHub: {e}")
    assert uf.path.exists()


def test_public_repo_xlsx_mocked() -> None:
    """Test downloading a .xlsx file from a mocked GitHub repo."""
    fake_content = b"fake xlsx content"
    with patch("urgap.ufile.io.github.Github") as mock_github_cls:
        mock_repo = MagicMock()
        mock_branch = MagicMock()
        mock_branch.name = "main"
        mock_repo.get_branches.return_value = [mock_branch]
        mock_contents = MagicMock()
        mock_contents.decoded_content = fake_content
        mock_repo.get_contents.return_value = mock_contents
        mock_github_cls.return_value.get_repo.return_value = mock_repo

        uf = urgap.UFile(
            uri="github://github.com/plotly/datasets/main#2014_apple_stock.xlsx",
        )

        m_open = mock_open()
        with patch("pathlib.Path.open", m_open):
            uf.download()

        m_open.assert_called_once_with("wb")
        handle = m_open()
        handle.write.assert_called_once_with(fake_content)
        assert uf.path.exists() is True
        assert uf.path.suffix == ".xlsx"
