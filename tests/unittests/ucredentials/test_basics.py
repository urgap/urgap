import os

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