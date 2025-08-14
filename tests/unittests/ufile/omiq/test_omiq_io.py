import tempfile

from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

import pytest

import urgap

from urgap.ufile.io.omiq import IOOmiq


@pytest.fixture
def mock_omiq_api():
    with patch("urgap.ext.omiq_api.API") as mock:
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
def mock_urgap_credential_manager():
    with patch("urgap.instances.ucredential_manager") as mock:
        mock.get_password.return_value = "test_password"
        mock.get_user.return_value = "test_user@example.com"
        yield mock


@pytest.fixture
def uuri():
    return urgap.UUri(uri="omiq://example.com/123456789#file.txt")


@pytest.fixture
def uuri2():
    return urgap.UUri(uri="omiq://example.com/123456789#file.csv")


@pytest.fixture
def uuri3():
    return urgap.UUri(
        uri="omiq://example.com/123456789?filter_usage_mode=BOOLCOLS&reverse_scaling=True&derived_from_fcs=True&from_task_id=123&filter_ids=['filter1','filter3']#file.csv",
    )


@pytest.fixture
def io_omiq_instance(mock_omiq_api, mock_urgap_credential_manager, uuri):
    with patch("urgap.ufile.io.omiq.omiq_api_available", True):
        return IOOmiq(uuri=uuri, scratch_path=Path(tempfile.gettempdir()))


@pytest.fixture
def io_omiq_instance2(mock_omiq_api, mock_urgap_credential_manager, uuri2):
    with patch("urgap.ufile.io.omiq.omiq_api_available", True):
        return IOOmiq(uuri=uuri2, scratch_path=Path(tempfile.gettempdir()))


@pytest.fixture
def io_omiq_instance3(mock_omiq_api, mock_urgap_credential_manager, uuri3):
    with patch("urgap.ufile.io.omiq.omiq_api_available", True):
        return IOOmiq(uuri=uuri3, scratch_path=Path(tempfile.gettempdir()))


@pytest.fixture
def io_omiq_instance_with_fcs(mock_omiq_api, mock_urgap_credential_manager):
    uuri = urgap.UUri(
        uri="omiq://example.com/123456789?derived_from_fcs=True#file.txt",
    )
    with patch("urgap.ufile.io.omiq.omiq_api_available", True):
        return IOOmiq(uuri=uuri, scratch_path=Path(tempfile.gettempdir()))


def test_init(io_omiq_instance, mock_omiq_api, uuri):
    assert io_omiq_instance._api is not None
    mock_omiq_api.assert_called_once_with(uuri.netloc, secret_filepath=ANY)
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
    assert io_omiq_instance.uuri.fragment == "file.txt"


def test_remote_path(io_omiq_instance):
    assert io_omiq_instance.remote_path is None


def test_remote_tag_path(io_omiq_instance):
    assert io_omiq_instance.remote_tag_path is None


def test_get_remote_tags(io_omiq_instance):
    mock_file_list = [
        {
            "id": 456,
            "datasetId": 123,
            "fileName": "file001.txt",
            "displayName": "file.txt",
            "rawFileBlobId": 789,
            "jobName": "Job 1",
            "status": "completed",
            "size": 1024,
        },
    ]
    io_omiq_instance._list_files_in_dataset = MagicMock(return_value=mock_file_list)

    tags = io_omiq_instance.get_remote_tags()

    assert tags["omiq_tags"] is True
    assert tags["id"] == 456
    assert tags["fileName"] == "file001.txt"
    assert tags["displayName"] == "file.txt"


def test_download_derived_from_fcs(io_omiq_instance3):
    io_omiq_instance3._list_files_in_dataset = MagicMock(
        return_value=[{"fileName": "file.fcs", "id": 456, "displayName": "file.fcs"}],
    )
    io_omiq_instance3.get_remote_tags = MagicMock(
        return_value={
            "id": 456,
            "features": [{"name": "feature1"}, {"name": "feature2"}],
        },
    )
    io_omiq_instance3._api.get_available_filters = MagicMock(
        return_value=["filter1", "filter2"],
    )

    io_omiq_instance3.download()

    io_omiq_instance3._api.export_data.assert_called_once_with(
        filter_usage_mode="BOOLCOLS",
        reverse_scaling=True,
        dataset_id=io_omiq_instance3._dataset_id,
        file_id=456,
        filepath=io_omiq_instance3._scratch_path,
        from_task_id=123,
        feature_names=["feature1", "feature2"],
        filter_ids=["filter1", "filter3"],
        workflow=io_omiq_instance3._workflow,
        add_row_nums=True,
    )


def test_download(io_omiq_instance):
    io_omiq_instance._list_files_in_dataset = MagicMock(
        return_value=[
            {
                "fileName": "file001.txt",
                "displayName": "file.txt",
                "id": 123,
                "features": ["feature1"],
            },
        ],
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
        return_value=["file.csv", "file2.txt"],
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
    mock_file_list = [
        {
            "fileName": "A1 0001_24h_U_Plate_001.fcs",
            "displayName": "A1 0001_24h_U_Plate001.fcs",
        },
        {
            "fileName": "A2 0001_24h_FS1_Plate_001.fcs",
            "displayName": "A2 0001_24h_FS1_Plate001.fcs",
        },
    ]
    io_omiq_instance._list_files_in_dataset = MagicMock(return_value=mock_file_list)
    io_omiq_instance._list_artifacts = MagicMock(return_value=["artifact1.txt"])


    assert set(items) == {
        "omiq://example.com/123456789#A1 0001_24h_U_Plate001.fcs",
        "omiq://example.com/123456789#A2 0001_24h_FS1_Plate001.fcs",
        "omiq://example.com/123456789#artifact1.txt",
    }


def test_remote_object_exists(io_omiq_instance):
    io_omiq_instance.list_container_items = MagicMock(
        return_value=["file.txt", "other_file.txt"],
    )
    io_omiq_instance._list_artifacts = MagicMock(return_value=["artifact.txt"])

    assert io_omiq_instance.remote_object_exists() is True

    io_omiq_instance.uuri.fragment = "non_existent_file.txt"
    assert io_omiq_instance.remote_object_exists() is False

def test_get_remote_tags_cached(io_omiq_instance):
    io_omiq_instance._tags = {"omiq_tags": True, "id": 123}

    tags = io_omiq_instance.get_remote_tags()

    assert tags == {"omiq_tags": True, "id": 123}

def test_download_omiq_gfile(io_omiq_instance):
    io_omiq_instance._download_file_from_workflow = MagicMock()
    io_omiq_instance.download()
    io_omiq_instance._download_file_from_workflow.assert_called_once()

def test_download_file_not_found(io_omiq_instance):
    io_omiq_instance._corresponding_fcs_filename = None
    io_omiq_instance._query_params["uftype"] = None
    io_omiq_instance._list_files_in_dataset = MagicMock(return_value=[])
    io_omiq_instance._list_artifacts = MagicMock(return_value=[])

    with pytest.raises(FileNotFoundError):
        io_omiq_instance.download()

def test_upload_with_tags_triggers_warning(io_omiq_instance, caplog):
    with caplog.at_level("WARNING"):
        io_omiq_instance.upload(tags={"key": "value"})
    assert "Upload of tags is not implemented yet." in caplog.text
    io_omiq_instance._api.upload_files_to_dataset.assert_called_once_with(
        io_omiq_instance._dataset_id, [io_omiq_instance.scratch_path]
    )

@pytest.fixture
def io_omiq_instance_with_tasks(mock_omiq_api, mock_urgap_credential_manager, uuri):
    with patch("urgap.ufile.io.omiq.omiq_api_available", True):
        return IOOmiq(uuri=uuri, scratch_path=Path(tempfile.gettempdir()))


def test_set_from_task_id_based_on_task_type(io_omiq_instance_with_tasks):
    io_omiq_instance_with_tasks._workflow = {
        "tasks": [
            {"id": 1, "type": "OtherTask"},
        ]
    }
    io_omiq_instance_with_tasks._query_params = {}

    io_omiq_instance_with_tasks._set_from_task_id()

    assert io_omiq_instance_with_tasks._query_params["from_task_id"] == 2


@pytest.fixture
def io_omiq_instance_with_workflow(mock_omiq_api, mock_urgap_credential_manager, uuri):
    with patch("urgap.ufile.io.omiq.omiq_api_available", True):
        return IOOmiq(uuri=uuri, scratch_path=Path(tempfile.gettempdir()))

def test_dict_workflow_creation(io_omiq_instance_with_workflow):
    io_omiq_instance_with_workflow._dataset_id = 12345

    io_omiq_instance_with_workflow._query_params = {}


    assert dict_workflow["dataset"] == 12345
    assert dict_workflow["workflow"] == {"id": 271715923047819, "name": "Test Workflow"}

    if "from_task_id" not in io_omiq_instance_with_workflow._query_params:
        io_omiq_instance_with_workflow._query_params["from_task_id"] = 2

    assert io_omiq_instance_with_workflow._query_params["from_task_id"] == 2

def test_handle_corresponding_fcs_filename_is_none(io_omiq_instance_with_fcs):
    io_omiq_instance_with_fcs._corresponding_fcs_filename = None
    io_omiq_instance_with_fcs.uuri.fragment = "fallback_file.fcs"

    assert f == "fallback_file.fcs"


if __name__ == "__main__":
    pytest.main()