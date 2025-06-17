from unittest.mock import MagicMock, mock_open, patch

import pytest

from github import GithubException


    )

    )


    uf_io_object.remote_object_exists = MagicMock(return_value=True)
    mock_file_sha = "existing_sha"
    uf_io_object.repo.get_contents.return_value.sha = mock_file_sha
    uf_io_object.repo.create_pull.return_value.number = 42

        uf_io_object.upload()

    # Assert
    uf_io_object.repo.create_git_ref.assert_called_once_with(
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
    )

    with (
        pytest.raises(RuntimeError, match="Failed to update the ufile"),
    ):
        uf_io_object.upload()


    uf_io_object.remote_object_exists = MagicMock(return_value=False)
    uf_io_object.repo.create_file.side_effect = GithubException(
    )

    with (
        pytest.raises(RuntimeError, match="Failed to add the ufile"),
    ):
        uf_io_object.upload()


    uf_io_object.remote_object_exists = MagicMock(return_value=False)
    uf_io_object.repo.create_file.return_value = None
    uf_io_object.repo.create_pull.side_effect = GithubException(400, "PR failed", None)

    with (
        pytest.raises(RuntimeError, match="Unable to create pull request"),
    ):
        uf_io_object.upload()