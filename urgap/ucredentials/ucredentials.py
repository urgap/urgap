"""UCredentials module of urgap."""

import contextlib
import importlib
import inspect
import json
import logging
import os
import pkgutil
from pathlib import Path
from jsonschema import validate
import urgap.ucredentials.io

logger = logging.getLogger(__name__)

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
        "password": {"type": "string"},
        "secure": {"type": "boolean"},
        "secret_store": {"type": "string"},
        "cloud_host_pid": {"type": "string"},
        "base_url": {"type": "string"},
    },
}


class UCredentialManager:
    """UCredentials Manager class.

    The credential Manager extracts the secrets from the secret store.

    The input is a dictionary with a "credentials" key, each entry specifying
    a secret backend and environment variable names for secrets (but not the secrets themselves).

    By default, it will try to read a `credentials_lookup.json` from $URGAP_HOME.
    """

    def __init__(
        self,
        json_path: str | os.PathLike | None = None,
        credentials_id_key: str = "{scheme}://{host}",
    ) -> None:
        """Initialize UCredentials.

        Args:
            json_path: Path to credentials.json. Defaults to $URGAP_HOME/credentials_lookup.json.
            credentials_id_key: How uniqueness is determined for entries.
        """
        super().__init__()

        self.available_io_classes: dict[str, type] = {}
        self._discover_secret_backends()

        self.ID_KEY = credentials_id_key
        self.ingested_credentials = {}
        self._extracted_secrets = {}

        for cred_entry in self.read_credentials(json_path=json_path):
            self.ingest_cred_entry(cred_entry)

        self._io = None

    def _discover_secret_backends(self) -> None:
        """Discover and register all credentials IO backend modules."""
        import urgap.ucredentials.io as io_namespace

        from urgap.ucredentials.io._base import IOBaseCreds

        for _finder, module_name, _is_pkg in pkgutil.iter_modules(
            io_namespace.__path__,
            prefix="urgap.ucredentials.io.",
        ):
            short_name = module_name.rsplit(".", 1)[-1]
            if short_name.startswith("_"):
                continue
            with contextlib.suppress(ImportError):
                module = importlib.import_module(module_name)
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, IOBaseCreds)
                        and obj is not IOBaseCreds
                        and obj.__module__ == module_name
                        and not inspect.isabstract(obj)
                    ):
                        self.available_io_classes[obj.SCHEME] = obj

    @property
    def io(self) -> urgap.ucredentials.io:
        """IO Property can be set with init_io_class()."""
        return self._io

    def init_io_class(
        self,
        secret_store: str,
        secret_id: str,
        **extra,
    ) -> urgap.ucredentials.io:
        """Initialize the secret backend handler."""
        if secret_store not in self.available_io_classes:
            msg = (
                f"IO class {secret_store} cannot be imported due to missing dependencies."
                "If needed use: pip install 'urgap[cloud]'"
            )
            raise ImportError(msg)
        io_class = self.available_io_classes[secret_store]
        try:
            self._io = io_class(secret_id=secret_id, **extra)
        except (TypeError, ValueError) as e:
            msg = f"Could not initialize secret backend '{secret_store}': {e}"
            logger.info(msg)
            raise

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
            logger.warning("Can only get user based on cred_entry or cred_key")
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
            logger.warning("Can only get password based on cred_entry or cred_key")
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

        if _cred_entry.get("cloud_host_pid") is not None:
            cloud_host_pid = _cred_entry["cloud_host_pid"]
        else:
            cloud_host_pid = _cred_entry.get("host", "localhost")

        reserved = {
            "description",
            "scheme",
            "host",
            "user",
            "password",
            "secure",
            "secret_store",
            "base_url",
            "cloud_host_pid",
        }
        extra = {k: v for k, v in _cred_entry.items() if k not in reserved}
        extra["cloud_host_pid"] = cloud_host_pid

        for keyname in ["user", "password"]:
            secret_id = _cred_entry[keyname]

            self.init_io_class(
                secret_store=_cred_entry.get("secret_store", "env"),
                secret_id=secret_id,
                **extra,
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
            logger.warning(msg)
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
        if cred_entry.get("base_url") is not None:
            return cred_entry["base_url"]
        try:
            c_key = self.ID_KEY.format(**cred_entry)
            logger.warning(
                "DeprecationWarning: 'scheme' + 'host' as identifier will be deprecated soon, "
                "please provide 'base_url' in credentials_lookup instead.",
            )
        except KeyError as e:
            msg = (
                f"Credential entry (fields: {sorted(cred_entry)}) cannot be "
                f"formatted into {self.ID_KEY}"
            )
            logger.warning(msg)
            raise KeyError(msg) from e
        return c_key

    def read_credentials(self, json_path: str | os.PathLike | None = None) -> dict:
        """Read from credentials_lookup.json.

        Args:
            json_path: Path to credentials.json. Defaults to $URGAP_HOME/credentials_lookup.json.

        Returns:
            List of credential dicts.
        """
        if json_path is None:
            json_path = Path(urgap.home) / "credentials_lookup.json"
        cred_json = {}
        if json_path.exists():
            with json_path.open() as uj:
                cred_json = json.load(uj)
        else:
            msg = f"{json_path} does not exist!"
            logger.warning(msg)
        return cred_json["credentials"]

    def write_credentials(
        self,
        json_path: str | os.PathLike | None = None,
        description: str = "Autogenerated Urgap Credential lookup",
    ) -> None:
        """Write credentials_lookup.json with all ingested credentials.

        Args:
            json_path: Path to json to be written.
            description: Description text to be included.

        Note: Will not write out the extracted credentials, only the credential_lookup.
        """
        if json_path is None:
            json_path = Path(urgap.home) / "credentials_lookup.json"
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
            logger.debug(msg)
