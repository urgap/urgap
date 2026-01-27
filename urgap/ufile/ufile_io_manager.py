"""UFileIOManager module of urgap2."""

import contextlib
import importlib


class UFileIOManager:
    """Manager for UFile IO backends.

    The UFileIOManager is responsible for detecting and managing which IO classes
    are available for UFile objects, mapping storage schemes to their respective implementations.
    """

    def __init__(self) -> None:
        """Initialize the UFile IO Manager.

        This will attempt to import all supported IO backend modules and store
        available ones in self.available_io_classes, mapping storage schemes to
        their implementation classes.
        """
        super().__init__()

        self.available_io_classes = {}
        io_modules_schema_map = {
            "_base": "_base",
            "azure_blob": "azure",
            "azure_datalake": "az-dl",
            "azure_smb": "az-smb",
            "file": "file",
            "ftp": "ftp",
            "github": "github",
            "google_storage": "gcs",
            "https": "https",
            "mylabdata": "mylabdata",
            "omiq": "omiq",
            "samba": "smb",
        }
        class_mappings = {
            "_base": "UIOBase",
            "azure": "IOAzureBlobStorage",
            "az-dl": "IOAzureDL",
            "az-smb": "IOAzureSMB",
            "file": "IOPython",
            "ftp": "IOFTP",
            "gcs": "IOGoogleCloudStorage",
            "github": "IOGithub",
            "https": "IOHTTPS",
            "mylabdata": "IOMyLabData",
            "omiq": "IOOmiq",
            "smb": "IOSMB",
        }
        for io_module, schema in io_modules_schema_map.items():
            with contextlib.suppress(ImportError):
                self.available_io_classes[schema] = getattr(
                    importlib.import_module(f"urgap.ufile.io.{io_module}"),
                    class_mappings[schema],
                )
