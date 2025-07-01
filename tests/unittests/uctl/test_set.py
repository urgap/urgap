import json

import urgap


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


def test_set_credentials(provide_changeable_credentials):

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