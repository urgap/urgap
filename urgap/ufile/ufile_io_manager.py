
import contextlib
import importlib


class UFileIOManager:

    """

    def __init__(self) -> None:
        super().__init__()

        self.available_io_classes = {}
        io_modules_schema_map = {
            "_base": "_base",
            "azure_blob": "azure",
            "azure_smb": "az-smb",
            "file": "file",
            "ftp": "ftp",
            "google_storage": "gcs",
            "https": "https",
            "mylabdata": "mylabdata",
            "omiq": "omiq",
            "samba": "smb",
        }
        for io_module, schema in io_modules_schema_map.items():
            with contextlib.suppress(ImportError):
                )