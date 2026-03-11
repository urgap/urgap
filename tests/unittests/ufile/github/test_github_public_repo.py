"""Unit tests for GitHub UFile functionality, including public repo and .xlsx tests."""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from github import GithubException

import urgap

# Mock IO
uf = urgap.UFile(
    uri="github://github.com/numpy/numpy/main#README.rst",
)
uf.io.target_branch_name = "fake_target_branch"
uf.io.source_branch = MagicMock()
uf.io.source_branch.commit.sha = "fake_sha"
uf.io.source_branch.name = "fake_source_branch"
uf.io.object_filepath = "some/path/to/file.txt"
uf.io.repo = MagicMock()
uf_io_object = uf.io


def test_list_container_items_from_numpy() -> None:
    """Test listing container items from a public repo."""
    ufile = urgap.UFile(
        uri="github://github.com/computational-ms/unify_idents/dev#README.rst",
    )
    assert ufile.path.exists()
    ufl = ufile.io.list_container_items()
    assert len(ufl) == 89
    assert all(
        isinstance(item, str)
        and item.startswith("github://github.com/computational-ms/unify_idents/dev#")
        for item in ufl
    )


def test_list_container_items_from_numpy_fails() -> None:
    """Test that listing container items raises an error for an invalid repo or branch."""
    ufile = urgap.UFile(
        uri="github://github.com/computational-ms/unify_idents/this-branch-does-not-exist#docs",
    )
    with pytest.raises(Exception, match=r".*"):
        ufile.list_container_items()


def test_github_public_repo() -> None:
    """Test remote object existence and download behavior in a mocked repo."""
    # Test the absence of file
    uf_io_object.repo.get_contents = MagicMock(
        side_effect=GithubException("Something went wrong"),
    )
    assert uf_io_object.remote_object_exists() is False

    # Test the file that exists
    uf_io_object.repo.get_contents = MagicMock(return_value=True)
    assert uf_io_object.remote_object_exists() is True

    # Test downloading the file
    uf_io_object.repo.get_contents.return_value = MagicMock(
        decoded_content=b"hello from github",
    )
    m = mock_open()
    with patch("pathlib.Path.open", m):
        uf_io_object.download()

    # Assert file write
    m.assert_called_once_with("w", encoding="utf-8")
    handle = m()
    handle.write.assert_called_once_with("hello from github")


def test_upload_updates_existing_file() -> None:
    """Test uploading updates an existing file."""
    uf_io_object.repo.create_git_ref.reset_mock()
    uf_io_object.repo.update_file.reset_mock()
    uf_io_object.repo.create_pull.reset_mock()
    uf_io_object.remote_object_exists = MagicMock(return_value=True)
    mock_file_sha = "existing_sha"
    uf_io_object.repo.get_contents.return_value.sha = mock_file_sha
    uf_io_object.repo.create_pull.return_value.number = 42
    mock_content = b"test content"

    with patch("pathlib.Path.open", mock_open(read_data=mock_content)):
        uf_io_object.upload()

    # Assert
    uf_io_object.repo.create_git_ref.assert_called_once_with(
        ref="refs/heads/fake_target_branch",
        sha="fake_sha",
    )
    uf_io_object.repo.update_file.assert_called_once_with(
        path="some/path/to/file.txt",
        message="New ufile is available",
        content=mock_content,
        sha=mock_file_sha,
        branch="fake_target_branch",
    )
    uf_io_object.repo.create_pull.assert_called_once()


def test_upload_creates_new_file() -> None:
    """Test uploading creates a new file if it does not exist."""
    uf_io_object.repo.create_git_ref.reset_mock()
    uf_io_object.repo.update_file.reset_mock()
    uf_io_object.repo.create_pull.reset_mock()
    uf_io_object.remote_object_exists = MagicMock(return_value=False)
    uf_io_object.repo.create_pull.return_value.number = 42
    mock_content = b"new file content"

    with patch("pathlib.Path.open", mock_open(read_data=mock_content)):
        uf_io_object.upload()

    # Assert
    uf_io_object.repo.create_git_ref.assert_called_once()
    uf_io_object.repo.create_file.assert_called_once_with(
        path="some/path/to/file.txt",
        message="New ufile is available",
        content=mock_content,
        branch="fake_target_branch",
    )
    uf_io_object.repo.create_pull.assert_called_once()


def test_upload_update_file_failure() -> None:
    """Test failure handling when updating a file fails."""
    uf_io_object.repo.create_git_ref.reset_mock()
    uf_io_object.repo.update_file.reset_mock()
    uf_io_object.repo.create_pull.reset_mock()
    uf_io_object.remote_object_exists = MagicMock(return_value=True)
    uf_io_object.repo.get_contents.return_value.sha = "sha"
    uf_io_object.repo.update_file.side_effect = GithubException(
        400,
        "Update failed",
        None,
    )

    with (
        patch("pathlib.Path.open", mock_open(read_data=b"data")),
        pytest.raises(RuntimeError, match="Failed to update the ufile"),
    ):
        uf_io_object.upload()


def test_upload_create_file_failure() -> None:
    """Test failure handling when creating a new file fails."""
    uf_io_object.repo.create_git_ref.reset_mock()
    uf_io_object.repo.update_file.reset_mock()
    uf_io_object.repo.create_pull.reset_mock()
    uf_io_object.remote_object_exists = MagicMock(return_value=False)
    uf_io_object.repo.create_file.side_effect = GithubException(
        400,
        "Create failed",
        None,
    )

    with (
        patch("pathlib.Path.open", mock_open(read_data=b"data")),
        pytest.raises(RuntimeError, match="Failed to add the ufile"),
    ):
        uf_io_object.upload()


def test_upload_create_pr_failure() -> None:
    """Test failure handling when pull request creation fails."""
    uf_io_object.repo.create_file.reset_mock()
    uf_io_object.repo.create_file.side_effect = None
    uf_io_object.repo.create_file.return_value = None

    uf_io_object.remote_object_exists = MagicMock(return_value=False)
    uf_io_object.repo.create_file.return_value = None
    uf_io_object.repo.create_pull.side_effect = GithubException(400, "PR failed", None)

    with (
        patch("pathlib.Path.open", mock_open(read_data=b"data")),
        pytest.raises(RuntimeError, match="Unable to create pull request"),
    ):
        uf_io_object.upload()


def test_public_repo_xlsx_download() -> None:
    """Test that a public GitHub repo containing a .xlsx file can be accessed.

    After download, uf.path.exists() should return True.
    """
    uf = urgap.UFile(
        uri="github://github.com/frictionlessdata/datasets/main#files/excel/sample-1-sheet.xlsx",
    )
    uf.download()
    assert uf.path.exists()
