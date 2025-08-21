import shutil

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from urgap.ufile.io.file import IOPython


def test_iopython_get_object():
    class DummyUURI:
        def get_file_remote_path(self):
            self.called = True
            return Path("/tmp/dummy_file.txt")

    iofile = IOPython.__new__(IOPython)
    iofile.uuri = DummyUURI()

    result = iofile.get_object()
    assert result == Path("/tmp/dummy_file.txt")
    assert iofile.uuri.called is True


def test_iopython_upload_raises_oserror(monkeypatch):
    class DummyUURI:
        def get_file_remote_path(self):
            return Path("/tmp/remote_file.txt")

        def get_file_remote_tag_path(self):
            return Path("/tmp/remote_file.txt.tag")

    iofile = IOPython.__new__(IOPython)
    iofile.uuri = DummyUURI()

    monkeypatch.setattr(
        IOPython, "scratch_path", property(lambda self: Path("/tmp/scratch_file.txt"))
    )

    def raise_oserror(src, dst):
        raise OSError("simulated copy error")

    monkeypatch.setattr(shutil, "copyfile", raise_oserror)

    with pytest.raises(OSError, match="Could not copy file"):
        iofile.upload(tags={"key": "value"})


def test_iopython_create_container(tmp_path, caplog):
    class DummyUURI:
        def get_file_remote_path(self):
            return tmp_path / "some_file.txt"

    iofile = IOPython.__new__(IOPython)
    iofile.uuri = DummyUURI()

    with caplog.at_level("DEBUG"):
        iofile.create_container(exist_ok=True)

    container_folder = iofile.uuri.get_file_remote_path().parent
    assert container_folder.exists()

    assert any("Creating" in record.message for record in caplog.records)


def test_list_container_items_permission_error(tmp_path, caplog):
    class DummyUURI:
        path = str(tmp_path)

        def get_container_name(self):
            return tmp_path.name

    dummy_file = tmp_path / "file.txt"
    dummy_file.write_text("hello")

    iofile = IOPython.__new__(IOPython)
    iofile.uuri = DummyUURI()

    with patch.object(Path, "is_file", side_effect=PermissionError):
        with caplog.at_level("DEBUG"):
            result = iofile.list_container_items()

    assert any("Cannot determine if" in record.message for record in caplog.records)

    assert result == []