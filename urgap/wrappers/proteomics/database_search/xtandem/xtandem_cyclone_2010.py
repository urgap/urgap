"""Urgap xtandem_cyclone_2010 wrapper."""

import urgap

from urgap.wrappers.proteomics.database_search.xtandem.xtandem_alanine import (
    xtandem_alanine as xtandem,
)


class xtandem_cyclone_2010(xtandem):
    """Urgap wrapper for the xtandem_cyclone_2010 search engine.

    X! Tandem is an open source software that can match tandem mass spectra with
    peptide sequences, in a process that has come to be known as protein identification.
    See publication provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "xtandem_cyclone_2010",
        "version": "cyclone_2010",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "20.02.2020",
        "api_port": 42715,
        "engine_type": ("db_search", "proteomics"),
        "platform_independent": False,
        "utranslation_style": "xtandem_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "tandem",
                    "urn": "darwin/arm64/xtandem_cyclone_2010.zip",
                    "urn_md5": "9a4a0edf8c7e86098d8cab7b2d8c32a0",
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "tandem",
                    "urn": "darwin/x86_64/xtandem_cyclone_2010.zip",
                    "urn_md5": "9a4a0edf8c7e86098d8cab7b2d8c32a0",
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "linux": {
                "arm64": {
                    "exe": "tandem.exe",
                    "urn": "linux/arm64/xtandem_cyclone_2010.zip",
                    "urn_md5": "4d9978deb634317f44fe028ad98ff87f",
                    # ^- build by hand - if urgap build package is used, then md5 7afb6cfa95805edd10291443ac48cc0b
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "tandem.exe",
                    "urn": "linux/x86_64/xtandem_cyclone_2010.zip",
                    "urn_md5": "4d9978deb634317f44fe028ad98ff87f",
                    # ^- build by hand - if urgap build package is used, then md5 7afb6cfa95805edd10291443ac48cc0b
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "win32": {
                "x86_64": {
                    "exe": "tandem.exe",
                    "urn": "win32/x86_64/xtandem_cyclone_2010.zip",
                    "urn_md5": "ac700922602d69651b9063d0564bf621",
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

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize xtandem_cyclone_2010 class."""
        super().__init__(*args, **kwargs)
