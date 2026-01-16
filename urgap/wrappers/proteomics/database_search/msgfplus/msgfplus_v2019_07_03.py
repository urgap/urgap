"""Urgap msgfplus_v2019_07_03 wrapper."""

import urgap

from urgap.wrappers.proteomics.database_search.msgfplus.msgfplus_2021_03_22 import (
    msgfplus_2021_03_22 as msgfplus,
)


class msgfplus_v2019_07_03(msgfplus):
    """Urgap wrapper for the msgfplus_v2019_07_03 search engine.

    MS-GF+ (aka MSGF+ or MSGFPlus) performs peptide identification by scoring MS/MS
    spectra against peptides derived from a protein sequence database. MS-GF+ is
    optimized for a variety of spectral types, i.e., combinations of fragmentation
    method, instrument, enzyme, and experimental protocols. See publication provided
    under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "msgfplus_v2019_07_03",
        "version": "v2019_07_03",
        "release_date": "03.07.2019",
        "api_port": 42712,
        "engine_type": ("db_search", "proteomics"),
        "platform_independent": True,  # !
        "utranslation_style": "msgfplus_style_1",
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "MSGFPlus.jar",
                    "urn": "platform_independent/arc_independent/msgfplus_v2019_07_03.zip",
                    "urn_md5": "30c3b9d3fd87afb946d93ad03521edb1",
                    "external_md5": None,
                    "external_url": None,
                },
            },
        },
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "requires": {
            "other_uftypes": {
                "other_dependencies": ("java",),
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.converter.PYMZML_MGF: {"min": 1, "max": 1},
            urgap.uftypes.proteomics.FASTA: {"min": 1, "max": 1},
            urgap.uftypes.proteomics.MODS_XML: {"min": 0, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.dbsearch.MSGFPLUS_MZID: {"min": 1, "max": 1},
        },
        "citation": """
            Kim, S., Mischerikow, N., Bandeira, N., Navarro, J. D., Wich, L., Mohammed, S., Heck, A. J. R., & Pevzner, P. A. (2010). The Generating Function of CID, ETD, and CID/ETD Pairs of Tandem Mass Spectra: Applications to Database Search.
            In Molecular Cellular Proteomics (Vol. 9, Issue 12, pp. 2840-2852). Elsevier BV. https://doi.org/10.1074/mcp.m110.003731
            """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize msgfplus_v2019_07_03 class."""
        super().__init__(*args, **kwargs)
