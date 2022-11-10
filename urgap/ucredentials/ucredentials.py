import json
from pathlib import Path


    """UCredentials Manager class.

    The credential Manager extracts the secrets from the secret store.


    """

    def __init__(
        self,

        Args:
        """

        self.ID_KEY = credentials_id_key



        Args:

        Returns:
        """
        else:


        Args:

        """


        Args:

        Returns:
        """

        """Add credentials to the manager.

        Args:
        """
        for cred_entry in credential_list:


        Args:

        Returns:
        """
        try:
            c_key = self.ID_KEY.format(**cred_entry)
        return c_key


        Args:

        Returns:
        """


        Args:

        """