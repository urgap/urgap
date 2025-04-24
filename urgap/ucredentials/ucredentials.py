
import contextlib
import importlib
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
        json_path: str | os.PathLike | None = None,
        credentials_id_key: str = "{scheme}://{host}",
    ) -> None:
        """Initialize UCredentials.

        Args:
        """
        super().__init__()

        self.available_io_classes = {}
        io_modules = (
            "echo",
            "env",
            "gcp",
        )
        for io_module in io_modules:
            with contextlib.suppress(ImportError):
                self.available_io_classes[io_module] = importlib.import_module(
                )

        self.ID_KEY = credentials_id_key
        self.ingested_credentials = {}
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
        cloud_host_pid: str | None = None,
        if secret_store not in self.available_io_classes:
            msg = (
                f"IO class {secret_store} cannot be imported due to missing dependencies."
            )
            raise ImportError(msg)
        if secret_store == "env":
            self._io = self.available_io_classes[secret_store].IOEnvCreds(
            )
        elif secret_store == "gcp":
            self._io = self.available_io_classes[secret_store].IOGCPCreds(
                secret_id=secret_id,
                project_id=cloud_host_pid,
                version_id="latest",
            )
        elif secret_store == "akv":
            self._io = self.available_io_classes[secret_store].IOAzureCreds(
                secret_id=secret_id,
                vault_name=cloud_host_pid,
            )
        elif secret_store == "echo":
            self._io = self.available_io_classes[secret_store].IOEchoCreds(
            )
        else:
            msg = (
                f"Don't know secret backend {secret_store}."
                f"Currently supported secret_stores are 'echo', 'env', 'gcp' and 'akv'."
            )

    def get_user(
        self,
        ce_or_ck: str | dict,
        force: bool = False,
    ) -> str | None:

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
        ce_or_ck: str | dict,
        force: bool = False,
    ) -> str | None:

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
    ) -> dict:

        Args:

        Returns:
        """
                raise KeyError(msg)
        return self._extracted_secrets[cred_key]

    def ingest_cred_entry(self, cred_entry: dict) -> None:

        Args:
        """
        cred_key = self.format_cred_key(cred_entry)
        cred_entry = self.validate_credential_entry(cred_entry)
        if cred_entry is not None:
            self.ingested_credentials[cred_key] = cred_entry
        else:
            msg = (
                f"The credentials for {cred_key} were not valid. Hence, "
                f"{cred_key} will not be ingested."
            )
        if cred_key in self._extracted_secrets:
            del self._extracted_secrets[cred_key]

    def validate_credential_entry(self, cred_entry: dict) -> dict:

        Args:

        Returns:
        """
        validate(instance=cred_entry, schema=DEFAULT_CREDENTIALS_SCHEME)
        return cred_entry

    def add_credentials(self, credential_list: list) -> None:
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
            msg = f"{cred_entry} cannot be formated into {self.ID_KEY}"
        return c_key

    def read_credentials(self, json_path: str | os.PathLike | None = None) -> dict:
        """Read from credentials_lookup.json.

        Args:

        Returns:
        """
        if json_path is None:
        cred_json = {}
                cred_json = json.load(uj)
        else:
            msg = f"{json_path} does not exist!"
        return cred_json["credentials"]

    def write_credentials(
        self,
        json_path: str | os.PathLike | None = None,
    ) -> None:

        Args:

        """
        if json_path is None:
            json.dump(
                {
                    "description": description,
                    "credentials": list(self.ingested_credentials.values()),
                },
                uj,
                indent=4,
            )
            msg = f"Wrote {json_path} containing {len(self.ingested_credentials)} entries."