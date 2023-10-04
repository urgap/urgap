import json



def load_credentials(scheme=None):
    with open(config_path) as fp:
        credentials = json.load(fp).get("credentials")
        fp.close()
    if scheme is None:
        return credentials


    creds = load_credentials()
    pw = "test"
    for entry in creds:
        scheme = entry.get("scheme")
        host = entry.get("host")
        if host.startswith("<"):
            continue
        new_creds = load_credentials(scheme=scheme)
        assert new_creds.get("password") == pw