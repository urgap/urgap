import urllib



class IOHTTPS(UIOBase):

        """Create new UIO class for processing https scheme.

        Args:
        """


        Returns:
        """

        """Get referenced URL.

        Returns:
        """

        """Download referenced remote object.

        """
        try:

        except urllib.error.URLError:
                "[ - HTTP - ] For OSX, make sure that certificates are installed (/Applications/Python 3.x/Install Certificates.command)",
            )


        """Verify referenced remote object exists.

        Returns:
        """
        try:
            exists = True
        except urllib.error.HTTPError:
            exists = False
        return exists