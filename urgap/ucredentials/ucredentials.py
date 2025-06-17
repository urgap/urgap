
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
        "user": {"type": ["string", "null"]},
        "secure": {"type": "boolean"},
        "secret_store": {"type": "string"},
        "cloud_host_pid": {"type": "string"},
    },
}


class UCredentialManager:
    """UCredentials Manager class.

    The credential Manager extracts the secrets from the secret store.

    The input is a dictionary with a "credentials" key, each entry specifying
    a secret backend and environment variable names for secrets (but not the secrets themselves).

    """

    def __init__(
        self,
        json_path: str | os.PathLike | None = None,
        credentials_id_key: str = "{scheme}://{host}",
    ) -> None:
        """Initialize UCredentials.

        Args:
            credentials_id_key: How uniqueness is determined for entries.
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
                    f".{io_module}",
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
        """Initialize the secret backend handler."""
        if secret_store not in self.available_io_classes:
            msg = (
                f"IO class {secret_store} cannot be imported due to missing dependencies."
            )
            raise ImportError(msg)
        if secret_store == "env":
            self._io = self.available_io_classes[secret_store].IOEnvCreds(
                secret_id=secret_id,
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
                secret_id=secret_id,
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
        """Access the user for a credential entry or key.

        Args:
            ce_or_ck: Credential entry dict or credentials key string.
            force: Force re-extraction from secret backend.

        Returns:
            The username if found, else None.
        """
        if isinstance(ce_or_ck, dict):
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
        """Access the password for a credential entry or key.

        Args:
            ce_or_ck: Credential entry dict or credentials key string.
            force: Force re-extraction from secret backend.

        Returns:
            The password if found, else None.
        """
        if isinstance(ce_or_ck, dict):
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
        """Extract secrets for a given credentials key.

        Args:
            cred_key: Key to extract.
            force: Force re-extraction from secret backend.

        Returns:
            Extracted credentials for the key.
        """
        if cred_key in self._extracted_secrets and not force:
            return self._extracted_secrets[cred_key]

        tmp = {}
        _cred_entry = self.ingested_credentials.get(cred_key)
        if _cred_entry is None:
            msg = f"{cred_key} could not be extracted - is missing!"
            raise KeyError(msg)

        if (_cred_entry["secret_store"] in ("gcp", "akv")) and (
            _cred_entry["cloud_host_pid"] is not None
        ):
            cloud_host_pid = _cred_entry["cloud_host_pid"]
        else:
            cloud_host_pid = _cred_entry.get("host", "localhost")

        for keyname in ["user", "password"]:
            secret_id = _cred_entry[keyname]

            self.init_io_class(
                secret_store=_cred_entry.get("secret_store", "env"),
                secret_id=secret_id,
                cloud_host_pid=cloud_host_pid,
            )

            if keyname == "user" and secret_id is None:
                tmp[keyname] = None
                continue

            secret = self.io.get_secret()
            if secret is None:
                msg = f"{secret_id} for {cred_key} is missing!"
                raise KeyError(msg)

            tmp[keyname] = secret
        self._extracted_secrets[cred_key] = tmp
        return self._extracted_secrets[cred_key]

    def ingest_cred_entry(self, cred_entry: dict) -> None:
        """Ingest a single credential entry into the manager.

        Args:
            cred_entry: Credential entry dict.
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
        """Validate a credential entry.

        Args:
            cred_entry: Credential entry.

        Returns:
            Validated entry.
        """
        validate(instance=cred_entry, schema=DEFAULT_CREDENTIALS_SCHEME)
        return cred_entry

    def add_credentials(self, credential_list: list) -> None:
        """Add credentials to the manager.

        Args:
            credential_list: List of credential entries.
        """
        for cred_entry in credential_list:
            self.ingest_cred_entry(cred_entry)

    def format_cred_key(self, cred_entry: dict) -> str:
        """Format the credential key based on self.ID_KEY.

        Args:
            cred_entry: Credential entry.

        Returns:
            Lookup key string.
        """
        try:
            c_key = self.ID_KEY.format(**cred_entry)
            msg = f"{cred_entry} cannot be formated into {self.ID_KEY}"
        return c_key

    def read_credentials(self, json_path: str | os.PathLike | None = None) -> dict:
        """Read from credentials_lookup.json.

        Args:

        Returns:
            List of credential dicts.
        """
        if json_path is None:
        cred_json = {}
        if json_path.exists():
            with json_path.open() as uj:
                cred_json = json.load(uj)
        else:
            msg = f"{json_path} does not exist!"
        return cred_json["credentials"]

    def write_credentials(
        self,
        json_path: str | os.PathLike | None = None,
    ) -> None:
        """Write credentials_lookup.json with all ingested credentials.

        Args:
            json_path: Path to json to be written.
            description: Description text to be included.

        Note: Will not write out the extracted credentials, only the credential_lookup.
        """
        if json_path is None:
        with json_path.open("w") as uj:
            json.dump(
                {
                    "description": description,
                    "credentials": list(self.ingested_credentials.values()),
                },
                uj,
                indent=4,
            )
            msg = f"Wrote {json_path} containing {len(self.ingested_credentials)} entries."