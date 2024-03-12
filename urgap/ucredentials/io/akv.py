
import logging

from azure.identity import DefaultAzureCredential



class IOAzureCreds(IOBaseCreds):
    """IO class interface Azure."""

        """Create new IOAzureCreds class."""
        self.secret_name = self.secret_id
        self.vault_name = kwargs["vault_name"]

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

        return secret