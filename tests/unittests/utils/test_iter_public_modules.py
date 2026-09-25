import sys
import types

import urgap.util as util_mod


def _install_fake_namespace(monkeypatch, package_name, module_names, private_names=()):
    fake_pkg = types.ModuleType(package_name)
    fake_pkg.__path__ = ["/dev/null"]
    monkeypatch.setitem(sys.modules, package_name, fake_pkg)

    entries = []
    for name in module_names:
        full_name = f"{package_name}.{name}"
        monkeypatch.setitem(sys.modules, full_name, types.ModuleType(full_name))
        entries.append((None, name, False))
    for name in private_names:
        full_name = f"{package_name}.{name}"
        monkeypatch.setitem(sys.modules, full_name, types.ModuleType(full_name))
        entries.append((None, name, False))
    entries.append((None, "a_subpackage", True))  # package entries must be skipped too

    monkeypatch.setattr(util_mod.pkgutil, "iter_modules", lambda path: entries)


def test_yields_each_public_module(monkeypatch):
    _install_fake_namespace(monkeypatch, "fake.iterpkg1", ["a", "b"])

    result = [mod.__name__ for mod in util_mod.iter_public_modules("fake.iterpkg1")]

    assert result == ["fake.iterpkg1.a", "fake.iterpkg1.b"]


def test_skips_subpackages(monkeypatch):
    _install_fake_namespace(monkeypatch, "fake.iterpkg2", ["a"])

    result = [mod.__name__ for mod in util_mod.iter_public_modules("fake.iterpkg2")]

    assert "fake.iterpkg2.a_subpackage" not in result


def test_skips_private_modules(monkeypatch):
    _install_fake_namespace(
        monkeypatch, "fake.iterpkg3", ["a"], private_names=["_internal"]
    )

    result = [mod.__name__ for mod in util_mod.iter_public_modules("fake.iterpkg3")]

    assert result == ["fake.iterpkg3.a"]


def test_missing_dependency_is_skipped_not_raised(monkeypatch, caplog):
    fake_pkg = types.ModuleType("fake.iterpkg4")
    fake_pkg.__path__ = ["/dev/null"]
    monkeypatch.setitem(sys.modules, "fake.iterpkg4", fake_pkg)
    monkeypatch.delitem(sys.modules, "fake.iterpkg4.broken", raising=False)

    real_import_module = util_mod.importlib.import_module

    def fake_import_module(name):
        if name == "fake.iterpkg4.broken":
            raise ImportError("no module named 'azure'")
        return real_import_module(name)

    monkeypatch.setattr(
        util_mod.pkgutil, "iter_modules", lambda path: [(None, "broken", False)]
    )
    monkeypatch.setattr(util_mod.importlib, "import_module", fake_import_module)

    with caplog.at_level("DEBUG"):
        result = list(util_mod.iter_public_modules("fake.iterpkg4"))

    assert result == []
    assert "broken" in caplog.text


def test_empty_namespace_yields_nothing(monkeypatch):
    fake_pkg = types.ModuleType("fake.iterpkg5")
    fake_pkg.__path__ = ["/dev/null"]
    monkeypatch.setitem(sys.modules, "fake.iterpkg5", fake_pkg)

    monkeypatch.setattr(util_mod.pkgutil, "iter_modules", lambda path: [])

    assert list(util_mod.iter_public_modules("fake.iterpkg5")) == []
