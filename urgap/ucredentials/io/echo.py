


class IOEchoCreds(IOBaseCreds):
    """IO class interface Echo."""

        """Create new IOEchoCreds class."""

    def get_secret(self) -> str:
        """Echo secret_id as secret for testing.

        Returns:
            Name of secret or better its known ID.
        """
        return self.secret_id