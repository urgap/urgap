import os
import types

import pytest

import urgap

from urgap.ucredentials.io._base import IOBaseCreds


def test_echo_init_works():
    us = urgap.UCredentialManager()
    us.init_io_class(secret_store="echo", secret_id="MITSURUGI")
    assert us.io.get_secret() == "MITSURUGI"

    us.init_io_class(secret_store="echo", secret_id="Precious")
    assert us.io.get_secret() == "Precious"


def test_env_init_works():
    os.environ["MITSURUGI"] = "rōnin"
    us = urgap.UCredentialManager()
    us.init_io_class(secret_store="env", secret_id="MITSURUGI")
    assert us.io.get_secret() == "rōnin"
    del os.environ["MITSURUGI"]


def test_unknown_secret_backend_logs_warning(caplog, monkeypatch):
    us = urgap.UCredentialManager()

    monkeypatch.setitem(us.available_io_classes, "fake_backend", object())

    with caplog.at_level("INFO"):
        us.init_io_class(secret_store="fake_backend", secret_id="dummy")
        assert "Don't know secret backend fake_backend" in caplog.text


def test_unknown_secret_backend_logs_warning(caplog, monkeypatch):
    us = urgap.UCredentialManager()

    monkeypatch.setitem(us.available_io_classes, "fake_backend", object())

    with caplog.at_level("INFO"):
        us.init_io_class(secret_store="fake_backend", secret_id="dummy")

    assert "Don't know secret backend fake_backend" in caplog.text


def test_get_user_warns_without_entry_or_key(caplog):
    ucm = urgap.UCredentialManager()

    with caplog.at_level("WARNING"):
        result = ucm.get_user()

    assert "Can only get user based on cred_entry or cred_key" in caplog.text
    assert result is None


def test_get_user_warns_without_entry_or_key(caplog):
    ucm = urgap.UCredentialManager()

    with caplog.at_level("WARNING"):
        result = ucm.get_user(None)

    assert "Can only get user based on cred_entry or cred_key" in caplog.text

    assert result is None


def test_get_password_warns_without_entry_or_key(caplog):
    ucm = urgap.UCredentialManager()

    with caplog.at_level("WARNING"):
        result = ucm.get_password(None)

    assert "Can only get password based on cred_entry or cred_key" in caplog.text
    assert result is None


def test_unknown_backend_hits_logger(caplog, monkeypatch):
    ucm = urgap.UCredentialManager()
    monkeypatch.setitem(ucm.available_io_classes, "unknown_backend", object())
    with caplog.at_level("INFO"):
        ucm.init_io_class(secret_store="unknown_backend", secret_id="dummy")
        assert any(
            "Don't know secret backend unknown_backend" in rec.message
            for rec in caplog.records
        )


def format_cred_key(self, cred_entry: dict) -> str:
    try:
        c_key = self.ID_KEY.format(**cred_entry)
    except KeyError:
        msg = f"{cred_entry} cannot be formated into {self.ID_KEY}"


def test_io_base_creds_get_secret_raises():
    creds = IOBaseCreds(secret_id="dummy")
    with pytest.raises(NotImplementedError) as excinfo:
        creds.get_secret()
    assert "needs to be implemented in the IOCreds class" in str(excinfo.value)


def test_missing_io_class_raises_importerror():
    us = urgap.UCredentialManager()
    with pytest.raises(ImportError) as e:
        us.init_io_class(secret_store="nonexistent_backend", secret_id="dummy")
    assert "cannot be imported due to missing dependencies" in str(e.value)


def test_gcp_io_class_init(monkeypatch):
    class DummyGCPClass:
        def __init__(self, secret_id, project_id, version_id):
            self.secret_id = secret_id
            self.project_id = project_id
            self.version_id = version_id

    dummy_module = types.SimpleNamespace(IOGCPCreds=DummyGCPClass)

    us = urgap.UCredentialManager()

    monkeypatch.setitem(us.available_io_classes, "gcp", dummy_module)

    us.init_io_class(secret_store="gcp", secret_id="dummy", cloud_host_pid="project123")

    assert isinstance(us.io, DummyGCPClass)
    assert us.io.secret_id == "dummy"
    assert us.io.project_id == "project123"
    assert us.io.version_id == "latest"


def test_akv_io_class_init(monkeypatch):
    class DummyAKV:
        def __init__(self, secret_id, vault_name):
            self.secret_id = secret_id
            self.vault_name = vault_name

    class DummyAKVModule:
        IOAzureCreds = DummyAKV

    us = urgap.UCredentialManager()
    monkeypatch.setitem(us.available_io_classes, "akv", DummyAKVModule)

    us.init_io_class(secret_store="akv", secret_id="dummy", cloud_host_pid="vault123")

    assert us._io.secret_id == "dummy"
    assert us._io.vault_name == "vault123"


def test_ingest_cred_entry_invalid_logs_warning(monkeypatch, caplog):
    us = urgap.UCredentialManager()

    monkeypatch.setattr(us, "validate_credential_entry", lambda x: None)

    cred_entry = {
        "description": "DemoInvalid",
        "scheme": "invalid-scheme",
        "host": "localhost",
        "user": "USER",
        "password": "PASS",
        "secure": True,
        "secret_store": "env",
    }

    with caplog.at_level("WARNING"):
        us.ingest_cred_entry(cred_entry)

    assert (
        f"The credentials for {us.ID_KEY.format(**cred_entry)} were not valid"
        in caplog.text
    )


def test_logger_warning_on_invalid_cred(monkeypatch, caplog):
    us = urgap.UCredentialManager()

    monkeypatch.setattr(us, "validate_credential_entry", lambda x: None)

    cred_entry = {
        "description": "DemoInvalid",
        "scheme": "invalid-scheme",
        "host": "localhost",
        "user": "USER",
        "password": "PASS",
        "secure": True,
        "secret_store": "env",
    }

    with caplog.at_level("WARNING"):
        us.ingest_cred_entry(cred_entry)

    assert (
        f"The credentials for {us.ID_KEY.format(**cred_entry)} were not valid"
        in caplog.text
    )


def format_cred_key(self, cred_entry: dict) -> str | None:
    """Format the credential key based on self.ID_KEY."""
    try:
        c_key = self.ID_KEY.format(**cred_entry)
    except KeyError:
        msg = f"{cred_entry} cannot be formated into {self.ID_KEY}"
        return None
    return c_key


def test_read_credentials_warns_for_missing_file(tmp_path, caplog):
    fake_path = tmp_path / "non_existent.json"

    with caplog.at_level("WARNING"):
        try:
            us.read_credentials(json_path=fake_path)
        except KeyError:
            pass

    assert f"{fake_path} does not exist!" in caplog.text

