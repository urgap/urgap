
import logging

import google.api_core.exceptions
import google_crc32c



class IOGCPCreds(IOBaseCreds):
    """IO class interface GCP."""

        """Create new IOGCPCreds class."""
        self.version_id = kwargs["version_id"]
        self.project_id = kwargs["project_id"]

        """Get secret from GCP secret Manager.

        Code adapted from:
        https://github.com/googleapis/python-secret-manager/blob/897cffe09ad97915f4b70617be839136de1416f4/samples/snippets/access_secret_version.py

        Returns:
            Secret from GCP secret Manager.
        """
        # Import the Secret Manager client library.
        secret = None
        client = None
        response = None

        try:
            client = secretmanager.SecretManagerServiceClient()
            response = client.access_secret_version(
                request={
                    "name": f"projects/{self.project_id}/secrets/{self.secret_id}/versions/{self.version_id}",
            )
        except (
            auth.exceptions.DefaultCredentialsError,
            google.api_core.exceptions.PermissionDenied,
        ):
            logging.warning("Secret could not be retrieved from GCP.")

        if client is not None and response is not None:
            # Verify payload checksum.
            crc32c = google_crc32c.Checksum()
            crc32c.update(response.payload.data)
            if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):

            secret = response.payload.data.decode("UTF-8")
        return secret