import tempfile


@pytest.fixture
def mock_omiq_api():
        mock.return_value.get_user.return_value = {
            "name": "Test User",
            "lastLoginTime": "2023-01-01",
        }
        mock.return_value.get_workflow.return_value = {
            "id": 271715923047819,
            "name": "ELX18861_TLR8_MyeloidHUPDBMXA_rPBMCs_01",
            "datasetId": 123,
            "tasks": [],
            "taskArtifacts": [{"taskId": 456, "file": "file.csv"}],
        }
        yield mock


@pytest.fixture
        mock.get_password.return_value = "test_password"
        mock.get_user.return_value = "test_user@example.com"
        yield mock


@pytest.fixture


@pytest.fixture


@pytest.fixture


@pytest.fixture


@pytest.fixture


    assert io_omiq_instance._api is not None
    assert io_omiq_instance._omiq_user_info == {
        "name": "Test User",
        "lastLoginTime": "2023-01-01",
    }
    assert io_omiq_instance._dataset_id == 123
    assert io_omiq_instance._workflow == {
        "id": 271715923047819,
        "name": "ELX18861_TLR8_MyeloidHUPDBMXA_rPBMCs_01",
        "datasetId": 123,
        "tasks": [],
        "taskArtifacts": [{"taskId": 456, "file": "file.csv"}],
    }


def test_remote_path(io_omiq_instance):
    assert io_omiq_instance.remote_path is None


def test_remote_tag_path(io_omiq_instance):
    assert io_omiq_instance.remote_tag_path is None


def test_get_remote_tags(io_omiq_instance):
    mock_file_list = [
        {
            "id": 456,
            "datasetId": 123,
            "rawFileBlobId": 789,
            "jobName": "Job 1",
            "status": "completed",
            "size": 1024,
    ]
    io_omiq_instance._list_files_in_dataset = MagicMock(return_value=mock_file_list)

    tags = io_omiq_instance.get_remote_tags()

    assert tags["omiq_tags"] is True
    assert tags["id"] == 456


    )
        return_value={
            "id": 456,
            "features": [{"name": "feature1"}, {"name": "feature2"}],
    )
    )


        file_id=456,
        from_task_id=123,
        feature_names=["feature1", "feature2"],
        filter_ids=["filter1", "filter3"],
        add_row_nums=True,
    )


def test_download(io_omiq_instance):
    io_omiq_instance._list_files_in_dataset = MagicMock(
    )

    io_omiq_instance.get_remote_tags = MagicMock(return_value={"id": 123})

    io_omiq_instance.download()

    io_omiq_instance._api.download_file.assert_called_once_with(
        dataset_id=io_omiq_instance._dataset_id,
        file_id=123,
        filepath=io_omiq_instance._scratch_path,
    )


def test_download_artifact(io_omiq_instance2):
    io_omiq_instance2._list_artifacts = MagicMock(
    )

    io_omiq_instance2.get_remote_tags = MagicMock(return_value={"id": 123})

    io_omiq_instance2.download()

    io_omiq_instance2._api.download_artifact.assert_called_once_with(
        workflow_id="123456789",
        task_id=456,
        artifact_name="file.csv",
        filepath=io_omiq_instance2._scratch_path,
    )


def test_list_container_items(io_omiq_instance):
    io_omiq_instance._list_files_in_dataset = MagicMock(return_value=mock_file_list)
    io_omiq_instance._list_artifacts = MagicMock(return_value=["artifact1.txt"])




def test_remote_object_exists(io_omiq_instance):
    io_omiq_instance.list_container_items = MagicMock(
    )
    io_omiq_instance._list_artifacts = MagicMock(return_value=["artifact.txt"])

    assert io_omiq_instance.remote_object_exists() is True

    assert io_omiq_instance.remote_object_exists() is False

if __name__ == "__main__":
    pytest.main()