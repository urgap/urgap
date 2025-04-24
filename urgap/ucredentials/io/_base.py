

class IOBaseCreds:
    """IOCreds Local class.

    All IOCreds classes inherit from this class.
    """

        """Create new IOBaseCreds instance with secret_id attribute set from kwargs.

        Args:
            **kwargs: Used to set secret_id attribute from key.
        """
        self.secret_id = kwargs["secret_id"]

        """Get_secret method is implemented in subclass."""
        msg = "This needs to be implemented in the IOCreds class"
        raise NotImplementedError(msg)