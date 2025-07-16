import json

from click.testing import CliRunner

import urgap

runner = CliRunner()


def test_check_if_config_key_value_is_valid():
    from urgap.uctl.set import _check_if_config_key_value_is_valid

    config = load_config()
    options = config.get("umeta", {}).get("options", [])
    if not options:
        options = ["sqlite3", "mongodb", "postgresql", "gcpsql"]
        config = {"umeta": {"options": options, "value": options[0]}}

    for option in options:
        assert _check_if_config_key_value_is_valid(config, "umeta", option) is True

    assert (
        _check_if_config_key_value_is_valid(config, "notarealkey", options[0]) is False
    )
    assert (
        _check_if_config_key_value_is_valid(config, "umeta", "notarealvalue") is False
    )

    config2 = {"valo": {"value": "valo"}}
    assert _check_if_config_key_value_is_valid(config2, "valo", "valo") is True

    _check_if_config_key_value_is_valid(config, "umeta", options[0], verbose=True)


def test_set_credentials_edge_cases():
    from urgap.uctl.set import set_credentials

    urgap.instances.ucredential_manager.ingested_credentials["notakey"] = None
    set_credentials(cred_key="notakey", password="secret", dry=True)


def test_set_credentials_click():
    from urgap.uctl.set import set_credentials_click

    runner = CliRunner()
    result = runner.invoke(
        set_credentials_click,
        [
            "test123",
            "--scheme",
            "x",
            "--host",
            "h",
            "--user",
            "u",
            "--password",
            "p",
            "--dry",
        ],
    )
    assert result.exit_code == 0


def test_check_if_config_key_value_is_valid_mode():
    from urgap.uctl.set import _check_if_config_key_value_is_valid

    config = load_config()

    assert _check_if_config_key_value_is_valid(config, "mode", "dev") is True
    assert _check_if_config_key_value_is_valid(config, "mode", "prod") is True
    assert _check_if_config_key_value_is_valid(config, "mode", "notamode") is False


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


def test_set_config(provide_changeable_config):
    from urgap.uctl.set import set_config

    test_objectives = load_config().get("umeta")["options"]
    for option in test_objectives:
        set_config(config_key="umeta", config_value=option, dry=False)
        new_umeta = load_config().get("umeta")["value"]
        assert new_umeta == option


def test_set_credentials(provide_changeable_credentials):
    from urgap.uctl.set import set_credentials

    creds = load_credentials()
    pw = "test"
    for entry in creds:
        scheme = entry.get("scheme")
        host = entry.get("host")
        if host.startswith("<"):
            continue
        cred_key = scheme + "://" + host
        set_credentials(cred_key=cred_key, password=pw, dry=False)
        new_creds = load_credentials(scheme=scheme)
        assert new_creds.get("password") == pw