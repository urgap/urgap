import sys
import types

import pytest

import urgap.util as util_mod


class DummyBase:
    """Stand-in base class, unrelated to any real urgap backend hierarchy."""


def _install_fake_namespace(monkeypatch, package_name, module_contents):
    """Register a fake namespace package with the given {short_name: [classes]} map."""
    fake_pkg = types.ModuleType(package_name)
    fake_pkg.__path__ = ["/dev/null"]
    monkeypatch.setitem(sys.modules, package_name, fake_pkg)

    short_names = []
    for short_name, classes in module_contents.items():
        full_name = f"{package_name}.{short_name}"
        mod = types.ModuleType(full_name)
        for cls in classes:
            cls.__module__ = full_name
            setattr(mod, cls.__name__, cls)
        monkeypatch.setitem(sys.modules, full_name, mod)
        short_names.append((None, short_name, False))

    monkeypatch.setattr(util_mod.pkgutil, "iter_modules", lambda path: short_names)


def test_valid_backend_is_discovered(monkeypatch):
    class GoodBackend(DummyBase):
        SCHEME = "good"

    _install_fake_namespace(monkeypatch, "fake.pkg1", {"good_mod": [GoodBackend]})

    result = util_mod.discover_backend_classes("fake.pkg1", DummyBase, "SCHEME")

    assert result == {"good": GoodBackend}


def test_class_without_marker_attr_is_skipped(monkeypatch):
    class NoScheme(DummyBase):
        pass

    _install_fake_namespace(monkeypatch, "fake.pkg2", {"no_scheme_mod": [NoScheme]})

    result = util_mod.discover_backend_classes("fake.pkg2", DummyBase, "SCHEME")

    assert result == {}


def test_unrelated_class_is_not_collected(monkeypatch):
    class Unrelated:
        SCHEME = "unrelated"

    _install_fake_namespace(monkeypatch, "fake.pkg3", {"unrelated_mod": [Unrelated]})

    result = util_mod.discover_backend_classes("fake.pkg3", DummyBase, "SCHEME")

    assert result == {}


def test_reexported_class_is_not_double_counted(monkeypatch):
    """A class merely imported into a second module (not defined there)
    must not be registered a second time under that module's name.
    """

    class RealBackend(DummyBase):
        SCHEME = "real"

    RealBackend.__module__ = "fake.pkg4.owner"

    owner_mod = types.ModuleType("fake.pkg4.owner")
    owner_mod.RealBackend = RealBackend

    reexport_mod = types.ModuleType("fake.pkg4.reexport")
    reexport_mod.RealBackend = RealBackend  # imported, not defined here

    fake_pkg = types.ModuleType("fake.pkg4")
    fake_pkg.__path__ = ["/dev/null"]

    monkeypatch.setitem(sys.modules, "fake.pkg4", fake_pkg)
    monkeypatch.setitem(sys.modules, "fake.pkg4.owner", owner_mod)
    monkeypatch.setitem(sys.modules, "fake.pkg4.reexport", reexport_mod)

    monkeypatch.setattr(
        util_mod.pkgutil,
        "iter_modules",
        lambda path: [(None, "owner", False), (None, "reexport", False)],
    )

    result = util_mod.discover_backend_classes("fake.pkg4", DummyBase, "SCHEME")

    assert result == {"real": RealBackend}


def test_duplicate_marker_value_raises_valueerror(monkeypatch):
    class BackendA(DummyBase):
        SCHEME = "dup"

    class BackendB(DummyBase):
        SCHEME = "dup"

    _install_fake_namespace(monkeypatch, "fake.pkg5", {"dup_mod": [BackendA, BackendB]})

    with pytest.raises(ValueError) as excinfo:
        util_mod.discover_backend_classes("fake.pkg5", DummyBase, "SCHEME")

    assert "dup" in str(excinfo.value)
    assert "BackendA" in str(excinfo.value)
    assert "BackendB" in str(excinfo.value)


def test_missing_dependency_is_skipped_not_raised(monkeypatch, caplog):
    fake_pkg = types.ModuleType("fake.pkg6")
    fake_pkg.__path__ = ["/dev/null"]
    monkeypatch.setitem(sys.modules, "fake.pkg6", fake_pkg)
    monkeypatch.delitem(sys.modules, "fake.pkg6.missing_dep", raising=False)

    real_import_module = util_mod.importlib.import_module

    def fake_import_module(name):
        if name == "fake.pkg6.missing_dep":
            raise ImportError("no module named 'azure'")
        return real_import_module(name)

    monkeypatch.setattr(
        util_mod.pkgutil,
        "iter_modules",
        lambda path: [(None, "missing_dep", False)],
    )
    monkeypatch.setattr(util_mod.importlib, "import_module", fake_import_module)

    with caplog.at_level("DEBUG"):
        result = util_mod.discover_backend_classes("fake.pkg6", DummyBase, "SCHEME")

    assert result == {}
    assert "missing_dep" in caplog.text
    assert "could not be imported" in caplog.text.lower()


def test_empty_namespace_returns_empty_dict(monkeypatch):
    fake_pkg = types.ModuleType("fake.pkg7")
    fake_pkg.__path__ = ["/dev/null"]
    monkeypatch.setitem(sys.modules, "fake.pkg7", fake_pkg)

    monkeypatch.setattr(util_mod.pkgutil, "iter_modules", lambda path: [])

    result = util_mod.discover_backend_classes("fake.pkg7", DummyBase, "SCHEME")

    assert result == {}


def test_private_module_is_skipped(monkeypatch):
    fake_pkg = types.ModuleType("fake.pkg8")
    fake_pkg.__path__ = ["/dev/null"]
    monkeypatch.setitem(sys.modules, "fake.pkg8", fake_pkg)

    real_import_module = util_mod.importlib.import_module
    called = []

    def tracking_import_module(name):
        called.append(name)
        return real_import_module(name)

    monkeypatch.setattr(
        util_mod.pkgutil,
        "iter_modules",
        lambda path: [(None, "_internal", False)],
    )
    monkeypatch.setattr(util_mod.importlib, "import_module", tracking_import_module)

    result = util_mod.discover_backend_classes("fake.pkg8", DummyBase, "SCHEME")

    assert result == {}
    assert "fake.pkg8._internal" not in called  # private module never imported
