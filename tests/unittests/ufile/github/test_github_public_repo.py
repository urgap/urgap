from unittest.mock import MagicMock, mock_open, patch

import pytest

from github import GithubException


    )

    )


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


    uf_io_object.remote_object_exists = MagicMock(return_value=False)
    uf_io_object.repo.create_pull.return_value.number = 42
    mock_content = b"new file content"

    with patch("pathlib.Path.open", mock_open(read_data=mock_content)):
        # Act
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


    uf_io_object.remote_object_exists = MagicMock(return_value=False)
    uf_io_object.repo.create_file.return_value = None
    uf_io_object.repo.create_pull.side_effect = GithubException(400, "PR failed", None)

    with (
        patch("pathlib.Path.open", mock_open(read_data=b"data")),
        pytest.raises(RuntimeError, match="Unable to create pull request"),
    ):
        uf_io_object.upload()