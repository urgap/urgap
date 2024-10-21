import tempfile

@pytest.fixture
def mock_omiq_api():
        mock.return_value.get_workflow.return_value = {
        }
        yield mock

@pytest.fixture
        yield mock

@pytest.fixture

@pytest.fixture

@pytest.fixture

@pytest.fixture

    assert io_omiq_instance._api is not None
    assert io_omiq_instance._dataset_id == 123
    assert io_omiq_instance._workflow == {
    }

def test_remote_path(io_omiq_instance):
    assert io_omiq_instance.remote_path is None

def test_remote_tag_path(io_omiq_instance):
    assert io_omiq_instance.remote_tag_path is None

def test_get_remote_tags(io_omiq_instance):
    mock_file_list = [
        {
    ]
    io_omiq_instance._list_files_in_dataset = MagicMock(return_value=mock_file_list)
    tags = io_omiq_instance.get_remote_tags()

def test_download(io_omiq_instance):

    io_omiq_instance.download()

    io_omiq_instance._api.download_file.assert_called_once_with(
        dataset_id=io_omiq_instance._dataset_id,
        file_id=123,
    )

def test_download_artifact(io_omiq_instance2):

    io_omiq_instance2.download()

    io_omiq_instance2._api.download_artifact.assert_called_once_with(
        task_id=456,
        filepath=io_omiq_instance2._scratch_path,
    )

def test_list_container_items(io_omiq_instance):
    io_omiq_instance._list_files_in_dataset = MagicMock(return_value=mock_file_list)

def test_remote_object_exists(io_omiq_instance):
    assert io_omiq_instance.remote_object_exists() is True
    assert io_omiq_instance.remote_object_exists() is False
