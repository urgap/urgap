import urllib



class IOHTTPS(UIOBase):




        try:

        except urllib.error.URLError:
                "[ - HTTP - ] For OSX, make sure that certificates are installed (/Applications/Python 3.x/Install Certificates.command)",
            )


        try:
            exists = True
        except urllib.error.HTTPError:
            exists = False
        return exists