"""Urgap xtandem_piledriver wrapper."""

import urgap

from urgap.wrappers.proteomics.database_search.xtandem.xtandem_alanine import (
    xtandem_alanine as xtandem,
)


class xtandem_piledriver(xtandem):
    """Urgap wrapper for the xtandem_piledriver search engine.

    X! Tandem is an open source software that can match tandem mass spectra with
    peptide sequences, in a process that has come to be known as protein identification.
    See publication provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "xtandem_piledriver",
        "version": "piledriver",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "01.04.2015",
        "api_port": 42717,
        "engine_type": ("db_search", "proteomics"),
        "platform_independent": False,
        "utranslation_style": "xtandem_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "tandem",
                    "urn": "darwin/arm64/xtandem_piledriver.zip",
                    "urn_md5": "1917031ae6afa5df66cf5e48f73c6389",
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "tandem",
                    "urn": "darwin/x86_64/xtandem_piledriver.zip",
                    "urn_md5": "1917031ae6afa5df66cf5e48f73c6389",
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "linux": {
                "arm64": {
                    "exe": "tandem.exe",
                    "urn": "linux/arm64/xtandem_piledriver.zip",
                    "urn_md5": "fc23d58748966faa067c7dfd572d9357",
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "tandem.exe",
                    "urn": "linux/x86_64/xtandem_piledriver.zip",
                    "urn_md5": "fc23d58748966faa067c7dfd572d9357",
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "win32": {
                "x86_64": {
                    "exe": "tandem.exe",
                    "urn": "win32/x86_64/xtandem_piledriver.zip",
                    "urn_md5": "9fa7f2ce8c17104d389f30019ba4aa38",
                    "external_md5": None,
                    "external_url": None,
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.converter.PYMZML_MGF: {"min": 1, "max": 1},
            urgap.uftypes.proteomics.FASTA: {"min": 1, "max": 1},
            urgap.uftypes.proteomics.MODS_XML: {"min": 0, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.dbsearch.XTANDEM_XML: {"min": 1, "max": 1},
        },
        "citation": """
        Craig, R., & Beavis, R. C. (2004). TANDEM: matching proteins with tandem mass spectra.
        In Bioinformatics (Vol. 20, Issue 9, pp. 1466-1467). Oxford University Press (OUP). https://doi.org/10.1093/bioinformatics/bth092
        """,
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize xtandem_piledriver class."""
        super().__init__(*args, **kwargs)
