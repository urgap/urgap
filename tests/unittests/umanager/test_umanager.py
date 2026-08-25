import types

import pytest

from urgap.umanager import UManager


class DummyBase:
    SCHEME: str


class DummyBackendA(DummyBase):
    SCHEME = "a"


class DummyBackendB(DummyBase):
    SCHEME = "b"


class DummyBackendADuplicate(DummyBase):
    """Same SCHEME as DummyBackendA -- used to test duplicate rejection."""

    SCHEME = "a"


def _make_manager(monkeypatch, classes):
    """Build a UManager subclass with discovery patched to return `classes`."""

    class DummyManager(UManager[DummyBase]):
        NAMESPACE_PACKAGE = "fake.namespace"
        BASE_CLASS = DummyBase
        MARKER_ATTR = "SCHEME"

    def fake_discover(namespace_package, base_class, marker_attr):
        registry = {}
        for cls in classes:
            key = getattr(cls, marker_attr)
            if key in registry:
                msg = f"Duplicate backend registration for {key!r}: {registry[key]} and {cls}"
                raise ValueError(msg)
            registry[key] = cls
        return registry

    monkeypatch.setattr("urgap.umanager.discover_backend_classes", fake_discover)
    return DummyManager


def test_single_backend_is_registered(monkeypatch):
    manager_cls = _make_manager(monkeypatch, [DummyBackendA])

    manager = manager_cls()

    assert manager.available_classes == {"a": DummyBackendA}


def test_multiple_backends_are_registered(monkeypatch):
    manager_cls = _make_manager(monkeypatch, [DummyBackendA, DummyBackendB])

    manager = manager_cls()

    assert manager.available_classes == {"a": DummyBackendA, "b": DummyBackendB}


def test_empty_discovery_yields_empty_registry(monkeypatch):
    manager_cls = _make_manager(monkeypatch, [])

    manager = manager_cls()

    assert manager.available_classes == {}


def test_duplicate_registration_key_raises_valueerror(monkeypatch):
    manager_cls = _make_manager(monkeypatch, [DummyBackendA, DummyBackendADuplicate])

    with pytest.raises(ValueError) as excinfo:
        manager_cls()

    assert "a" in str(excinfo.value)
    assert "DummyBackendA" in str(excinfo.value)
    assert "DummyBackendADuplicate" in str(excinfo.value)