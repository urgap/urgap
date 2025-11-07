import pytest

from urgap.ufile.io._base import UIOBase


class DummyUUri:
    def get_container_name(self):
        return "container"

    def get_object_name(self):
        return "object.txt"

    @property
    def storage_uri(self):
        return "dummy://storage"


def test_download_raises_notimplementederror():
    uio = UIOBase(uuri=DummyUUri())
    with pytest.raises(NotImplementedError) as exc:
        uio.download()
    assert "This needs to be implemented in the UIO class" in str(exc.value)


def test_upload_raises_notimplementederror():
    uio = UIOBase(uuri=DummyUUri())
    with pytest.raises(NotImplementedError) as exc:
        uio.upload()
    assert "This needs to be implemented in the UIO class" in str(exc.value)
