import pytest

import urgap

from urgap.umeta.io.dummy import UMeta


def test_set_umeta_fails_module_not_found_error():
    with pytest.raises(ModuleNotFoundError):
        um = urgap.UMeta(io="Mitsurugi")
        um.io


def test_umeta_dummy_init():
    um = UMeta()
    assert um.name == "UMeta for test purposes"
    assert hasattr(um, "load")
    assert hasattr(um, "save")
    assert hasattr(um, "umeta_exists")


def test_umeta_dummy_load():
    um = UMeta()
    data = um.load()
    assert isinstance(data, dict)
    assert "history" in data
    assert "urun_dict" in data
    assert data["history"] == []
    assert data["urun_dict"] == {}


def test_umeta_dummy_umeta_exists():
    um = UMeta()
    assert um.umeta_exists() is False


def test_umeta_dummy_save():
    um = UMeta()
    # save should not raise error even if umeta is None or dict
    um.save()
    um.save({"history": [1], "urun_dict": {"key": "value"}})
