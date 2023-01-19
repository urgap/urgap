import json
import logging
from pathlib import Path




class UCredentialManager:
    """UCredentials Manager class.

    The credential Manager extracts the secrets from the secret store.


    """

    def __init__(
        self,
        """Initialize UCredentials.

        Args:
        """

        self.ID_KEY = credentials_id_key
        self._extracted_secrets = {}

        for cred_entry in self.read_credentials(json_path=json_path):
            self.ingest_cred_entry(cred_entry)


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


        Args:

        Returns:
        """
        return self._extracted_secrets[cred_key]


        Args:
        """
        cred_key = self.format_cred_key(cred_entry)
        cred_entry = self.validate_credential_entry(cred_entry)
        if cred_entry is not None:
        else:
                f"The credentials for {cred_key} were not valid. Hence, "
                f"{cred_key} will not be ingested."
            )
            del self._extracted_secrets[cred_key]


        Args:

        Returns:
        """

        """Add credentials to the manager.

        Args:
        """
        for cred_entry in credential_list:
            self.ingest_cred_entry(cred_entry)


        Args:

        Returns:
        """
        try:
            c_key = self.ID_KEY.format(**cred_entry)
        return c_key

        """Read from credentials_lookup.json.

        Args:

        Returns:
        """
        if json_path is None:
        cred_json = {}
                cred_json = json.load(uj)
        else:
        return cred_json["credentials"]

    def write_credentials(
        self,

        Args:

        """
        if json_path is None:
            json.dump(
                {
                    "description": description,
                },
                uj,
                indent=4,
            )