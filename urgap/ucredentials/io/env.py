import os


    """IO class interface Env."""

        """Create new IOEnvCreds class."""

    def get_secret(self) -> str:
        """Extract Secret from ENV for secret_id.

        Returns:
            Name of secret or better its known ID or None if no secret_id in ENV.
        """
        return os.environ.get(self.secret_id, None)