"""Urgap xtandem_sledgehammer wrapper."""

import urgap

from urgap.wrappers.proteomics.database_search.xtandem.xtandem_alanine import (
    xtandem_alanine as xtandem,
)


class xtandem_sledgehammer(xtandem):
    """Urgap wrapper for the xtandem_sledgehammer search engine.

    X! Tandem is an open source software that can match tandem mass spectra with
    peptide sequences, in a process that has come to be known as protein identification.
    See publication provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "xtandem_sledgehammer",
        "version": "sledgehammer",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "20.02.2020",
        "api_port": 42718,
        "engine_type": ("db_search", "proteomics"),
        "platform_independent": False,
        "utranslation_style": "xtandem_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "tandem",
                    "urn": "darwin/arm64/xtandem_sledgehammer.zip",
                    "urn_md5": "b029ce1eca5f19b5869d0eeaa14b56f9",
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "tandem",
                    "urn": "darwin/x86_64/xtandem_sledgehammer.zip",
                    "urn_md5": "b029ce1eca5f19b5869d0eeaa14b56f9",
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "linux": {
                "arm64": {
                    "exe": "tandem.exe",
                    "urn": "linux/arm64/xtandem_sledgehammer.zip",
                    "urn_md5": "769d1c461de4bd0ebf563ed012a4b065",
                    # ^- build by hand - if urgap build package is used, then md5 b479f6dab08d4031334ea2609d1a3893
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "tandem.exe",
                    "urn": "linux/x86_64/xtandem_sledgehammer.zip",
                    "urn_md5": "769d1c461de4bd0ebf563ed012a4b065",
                    # ^- build by hand - if urgap build package is used, then md5 b479f6dab08d4031334ea2609d1a3893
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "win32": {
                "x86_64": {
                    "exe": "tandem.exe",
                    "urn": "win32/x86_64/xtandem_sledgehammer.zip",
                    "urn_md5": "45364036dfd7c4b20e7f5727eb33294e",
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
        """Initialize xtandem_sledgehammer class."""
        super().__init__(*args, **kwargs)
