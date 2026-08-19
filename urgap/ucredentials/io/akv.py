"""Azure credentials subclass of urgap's IOCreds submodule."""

import logging

from typing import ParamSpec

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from urgap.ucredentials.io._base import IOBaseCreds

P = ParamSpec("P")
logger = logging.getLogger(__name__)


class IOAzureCreds(IOBaseCreds):
    """IO class interface Azure."""

    SCHEME = "akv"

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new IOAzureCreds class."""
        super().__init__(**kwargs)
        self.secret_name = self.secret_id
        self.vault_name = kwargs["cloud_host_pid"]

    def get_secret(self) -> str:
        """Get secret from Azure Key Vault.

        Returns:
            Secret from Azure Key Vault.
        """
        secret = None

        try:
            credential = DefaultAzureCredential()
            client = SecretClient(
                vault_url=f"https://{self.vault_name}.vault.azure.net",
                credential=credential,
            )

            secret = client.get_secret(self.secret_name).value
        except (ResourceNotFoundError, HttpResponseError):
            logger.warning("Secret could not be retrieved from Azure.")

        return secret
