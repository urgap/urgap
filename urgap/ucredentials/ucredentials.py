import json
import logging
import os
from pathlib import Path

from jsonschema import validate


DEFAULT_CREDENTIALS_SCHEME = {
    "type": "object",
    "maxItems": 8,
    "required": [
        "description",
        "scheme",
        "host",
        "user",
        "password",
        "secure",
        "secret_store",
    ],
    "properties": {
        "description": {"type": "string"},
        "scheme": {"type": "string"},
        "host": {"type": "string"},
        "secure": {"type": "boolean"},
        "secret_store": {"type": "string"},
        "cloud_host_pid": {"type": "string"},
    },
}


class UCredentialManager:
    """UCredentials Manager class.

    The credential Manager extracts the secrets from the secret store.


    """

    def __init__(
        self,
        credentials_id_key: str = "{scheme}://{host}",
        """Initialize UCredentials.

        Args:
        """

        self.ID_KEY = credentials_id_key
        self._extracted_secrets = {}

        for cred_entry in self.read_credentials(json_path=json_path):
            self.ingest_cred_entry(cred_entry)

        self._io = None

    @property
        """IO Property can be set with init_io_class()."""
        return self._io

    def init_io_class(
        self,
        secret_store: str,
        secret_id: str,
        if secret_store == "env":
        elif secret_store == "gcp":
                secret_id=secret_id,
                project_id=cloud_host_pid,
                version_id="latest",
            )
        elif secret_store == "akv":
                secret_id=secret_id,
                vault_name=cloud_host_pid,
            )
        else:
                f"Don't know secret backend {secret_store}."
            )

    def get_user(
        self,
        force: bool = False,

        Args:

        Returns:
        """
            cred_key = self.format_cred_key(ce_or_ck)
            user = self.extract_credentials(cred_key, force=force)["user"]
        elif isinstance(ce_or_ck, str):
            user = self.extract_credentials(ce_or_ck, force=force)["user"]
        else:
            user = None
        return user

    def get_password(
        self,
        force: bool = False,

        Args:

        Returns:
        """
            cred_key = self.format_cred_key(ce_or_ck)
            password = self.extract_credentials(cred_key, force=force)["password"]
        elif isinstance(ce_or_ck, str):
            password = self.extract_credentials(ce_or_ck, force=force)["password"]
        else:
            password = None
        return password

    def extract_credentials(
        self,
        cred_key: str,
        force: bool = False,

        Args:

        Returns:
        """
        return self._extracted_secrets[cred_key]


        Args:
        """
        cred_key = self.format_cred_key(cred_entry)
        cred_entry = self.validate_credential_entry(cred_entry)
        if cred_entry is not None:
        else:
                f"The credentials for {cred_key} were not valid. Hence, "
                f"{cred_key} will not be ingested."
            )
            del self._extracted_secrets[cred_key]

    def validate_credential_entry(self, cred_entry: dict) -> dict:

        Args:

        Returns:
        """
        validate(instance=cred_entry, schema=DEFAULT_CREDENTIALS_SCHEME)
        return cred_entry

        """Add credentials to the manager.

        Args:
        """
        for cred_entry in credential_list:
            self.ingest_cred_entry(cred_entry)

    def format_cred_key(self, cred_entry: dict) -> str:

        Args:

        Returns:
        """
        try:
            c_key = self.ID_KEY.format(**cred_entry)
        return c_key

        """Read from credentials_lookup.json.

        Args:

        Returns:
        """
        if json_path is None:
        cred_json = {}
                cred_json = json.load(uj)
        else:
        return cred_json["credentials"]

    def write_credentials(
        self,

        Args:

        """
        if json_path is None:
            json.dump(
                {
                    "description": description,
                },
                uj,
                indent=4,
            )