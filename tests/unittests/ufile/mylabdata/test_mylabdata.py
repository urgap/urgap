"""Unit tests for urgap.ufile.io.mylabdata.IOMyLabData."""

import json

from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

import urgap

from urgap.ufile.io.mylabdata import IOMyLabData


class DummyUuri:
    """Dummy UURI class for testing purposes."""

    def __init__(self) -> None:
        """Initialize DummyUuri with default test values."""
        self.user: str = "user1"
        self.password: str = "pass1"
        self.netloc: str = "example.com"
        self.path: str = "bucket/in/mld"
        self.fragment: str = "file.txt"
        self.storage_uri: str = "https://storage.example.com"

    def get_container_name(self) -> str:
        """Return the container path."""
        return self.path

    def get_object_name(self) -> str:
        """Return the object name."""
        return self.fragment

    def get_mylabdata_api_url(self) -> str:
        """Return the API URL."""
        return "https://api.example.com"

    def get_mylabdata_api_url_files(self) -> str:
        """Return the API files URL."""
        return "https://files.example.com"

    @property
    def mylabdata_url(self) -> str:
        """Return the full MyLabData URL."""
        return f"https://files.example.com/{self.path}/{self.fragment}"


def make_response(
    content: bytes = b"{}",
    status_code: int = 200,
    json_data: dict[str, Any] | None = None,
) -> Mock:
    """Create a mocked requests.Response object for testing."""
    mock = Mock()
    mock.status_code = status_code
    mock.content = content
    if json_data is not None:
        mock.json.return_value = json_data
    else:
        mock.json.return_value = json.loads(content.decode("utf-8"))
    return mock


@pytest.fixture(autouse=True)
def patch_requests_for_all(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch requests.post and requests.get globally for all tests."""

    def fake_post(*_args: object, **_kwargs: object) -> Mock:
        return make_response(
            json_data={"data": {"token": "dummy-token"}},
            status_code=200,
        )

    def fake_get(*_args: object, **_kwargs: object) -> Mock:
        return make_response(status_code=200, content=b"{}")

    monkeypatch.setattr(
        "urgap.ufile.io.mylabdata.requests.post",
        fake_post,
    )
    monkeypatch.setattr(
        "urgap.ufile.io.mylabdata.requests.get",
        fake_get,
    )


@pytest.fixture
def dummy_obj(tmp_path: Path) -> IOMyLabData:
    """Return a dummy IOMyLabData object with a temporary scratch file."""
    u = DummyUuri()
    scratch = tmp_path / "scratch.txt"
    scratch.write_bytes(b"hello world")
    return IOMyLabData(uuri=u, scratch_path=scratch)


def test_get_token_bearer_failure() -> None:
    """Test that a 401 response raises ConnectionError when getting token."""
    with patch("urgap.ufile.io.mylabdata.requests.post") as mock_post:
        mock_post.return_value = make_response(status_code=401)
        with pytest.raises(ConnectionError):
            IOMyLabData(uuri=DummyUuri(), scratch_path=Path(__file__))


def test_get_remote_tags_success(dummy_obj: IOMyLabData) -> None:
    """Test retrieving remote tags successfully."""
    sample = {"tag1": "value1"}
    with patch("urgap.ufile.io.mylabdata.requests.get") as mock_get:
        mock_get.return_value = make_response(
            content=json.dumps(sample).encode("utf-8"),
            status_code=200,
        )
        tags = dummy_obj.get_remote_tags()
        assert tags == sample


def test_upload_file_conflict(dummy_obj: IOMyLabData) -> None:
    """Test uploading a file that results in a 409 conflict."""
    dummy_obj.scratch_path.parent.mkdir(parents=True, exist_ok=True)
    dummy_obj.scratch_path.write_bytes(b"hello world")

    with patch("urgap.ufile.io.mylabdata.requests.post") as mock_post:
        mock_post.return_value = make_response(status_code=409)
        resp = dummy_obj.upload()
    assert resp.status_code == 409


def test_upload_file_error(dummy_obj: IOMyLabData) -> None:
    """Test uploading a file that results in a server error."""
    with patch("urgap.ufile.io.mylabdata.requests.post") as mock_post:
        mock_post.return_value = make_response(status_code=500)
        with pytest.raises(ValueError, match=r"(?i)(?:error|failed|500)"):
            dummy_obj.upload()


def test_upload_tag_conflict(dummy_obj: IOMyLabData) -> None:
    """Test uploading tags with a conflict on the second request."""
    with patch("urgap.ufile.io.mylabdata.requests.post") as mock_post:
        mock_post.side_effect = [
            make_response(status_code=200),
            make_response(status_code=409),
        ]
        resp = dummy_obj.upload(tags={"k": "v"})
        assert resp.status_code == 200


def test_upload_tag_error(dummy_obj: IOMyLabData) -> None:
    """Test uploading tags that triggers a server error."""
    with patch("urgap.ufile.io.mylabdata.requests.post") as mock_post:
        mock_post.side_effect = [
            make_response(status_code=200),
            make_response(status_code=500),
        ]
        with pytest.raises(ValueError, match=r"(?i)500|error|upload failed"):
            dummy_obj.upload(tags={"k": "v"})


def test_append_container_objects_and_list(dummy_obj: IOMyLabData) -> None:
    """Test appending container objects with and without hashes."""
    files = [
        {"checksum": "c1", "downloadUrl": "https://a/b/c/d/file1.txt"},
        {"checksum": "c2", "downloadUrl": "https://a/b/c/d/file2.txt"},
    ]
    result = dummy_obj.append_container_objects(
        full_string=True,
        with_hashes=True,
        files=files,
        container_objects=None,
    )
    assert len(result) == 2

    result2 = dummy_obj.append_container_objects(
        full_string=False,
        with_hashes=False,
        files=files,
        container_objects=None,
    )
    assert len(result2) == 2


def test_list_container_items_filter_regex(dummy_obj: IOMyLabData) -> None:
    """Test filtering container items using a regex pattern."""
    files = [
        {"checksum": "c1", "downloadUrl": "https://a/b/c/d/foo.txt"},
        {"checksum": "c2", "downloadUrl": "https://a/b/c/d/bar.txt"},
    ]
    with patch("urgap.ufile.io.mylabdata.requests.get") as mock_get:
        mock_get.return_value = make_response(
            json_data={"data": {"files": files, "nextPage": ""}},
            status_code=200,
        )
        items = dummy_obj.list_container_items(
            pattern="foo",
            full_string=True,
            with_hashes=False,
        )
        assert any("foo" in name for name in items)
        assert all("bar" not in name for name in items)


def test_mylabdata_url_encoding() -> None:
    """Test proper URL encoding for MyLabData URLs."""
    uf = urgap.UFile("mylabdata://some/bucket/in/mld#some/file.txt")
    assert uf.uuri.get_mylabdata_api_url_files() == "https://some/files"
    assert uf.uuri.mylabdata_url == "https://some/files/bucket/in/mld/some%2Ffile.txt"

    uf2 = urgap.UFile("mylabdata://some/bucket/in/mld#some/filewith#.txt")
    assert (
        uf2.uuri.mylabdata_url
        == "https://some/files/bucket/in/mld/some%2Ffilewith%23.txt"
    )

    uf3 = urgap.UFile("mylabdata://some/bucket/in/mld#some/file with spaces/#=4.txt")
    assert (
        uf3.uuri.mylabdata_url
        == "https://some/files/bucket/in/mld/some%2Ffile%20with%20spaces%2F%23%3D4.txt"
    )