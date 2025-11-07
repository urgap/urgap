import json
import logging

from click.testing import CliRunner

import urgap

runner = CliRunner()


def test_show_credentials_not_found(caplog):
    from urgap.uctl.show import show_credentials

    fake_key = "somerandomtest://abc"
    with caplog.at_level(logging.INFO):
        show_credentials(fake_key)
    assert "No credentials found for key" in caplog.text


def test_show_config_json_output(caplog):
    from urgap.uctl.show import show_config_click

    with caplog.at_level(logging.INFO):
        runner.invoke(show_config_click, ["--output", "json"])
    assert "{" in caplog.text and "}" in caplog.text


def test_show_credentials_click_exists(caplog):
    from urgap.uctl.show import show_credentials_click

    creds = load_credentials()
    cred = None
    for entry in creds:
        scheme = entry.get("scheme")
        host = entry.get("host")
        if not host.startswith("<"):
            cred = scheme + "://" + host
            break
    if cred:
        with caplog.at_level(logging.INFO):
            runner.invoke(show_credentials_click, [cred])
        assert "Credential key" in caplog.text


def load_config():
    config_path = urgap.home / "urgap.json"
    with open(config_path) as fp:
        config = json.load(fp)
        fp.close()
    return config


def load_credentials(scheme=None):
    config_path = urgap.home / "credentials_lookup.json"
    with open(config_path) as fp:
        credentials = json.load(fp).get("credentials")
        fp.close()
    if scheme is None:
        return credentials
    for creds in credentials:
        if scheme == creds.get("scheme", None):
            return creds


def test_show_config(caplog):
    from urgap.uctl.show import show_config_click

    config = load_config()
    umeta = config.get("umeta")["value"]
    hash_algorithm = config.get("hash_algorithm")["value"]
    with caplog.at_level(logging.INFO):
        runner.invoke(show_config_click)
    assert f"'value': '{hash_algorithm}'" in caplog.text
    assert f"'value': '{umeta}'" in caplog.text


def test_show_credentials():
    from urgap.uctl.show import show_credentials

    creds = load_credentials()
    for entry in creds:
        scheme = entry.get("scheme")
        host = entry.get("host")
        if host.startswith("<"):
            continue
        cred_key = scheme + "://" + host
        show_credentials(cred_key=cred_key)
