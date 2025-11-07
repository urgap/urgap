"""Urgap flash_lfq_1_2_3 wrapper."""

import csv
import ctypes
import sys

import urgap

bits = ctypes.sizeof(ctypes.c_long) * 8
max_long = (2 ** (bits - 1)) - 1

csv.field_size_limit(min(sys.maxsize, max_long))

from urgap.wrappers.proteomics.quantification.flash_lfq.flash_lfq_1_2_0 import (
    flash_lfq_1_2_0 as flash_lfq,
)


class flash_lfq_1_2_3(flash_lfq):
    """Urgap wrapper for the flash_lfq_1_2_3 resource.

    FlashLFQ is a computer program for high-speed label-free quantification of peptides
    following a search of bottom-up mass spectrometry data. See publication
    provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "flash_lfq_1_2_3",
        "version": "1.2.3",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "06.09.2022",
        "api_port": 42725,
        "engine_type": ("quantification", "proteomics"),
        "platform_independent": True,  # dotnet6 :)
        "requires": {
            "other_uftypes": {
                "other_dependencies": ("dotnet6",),
            },
        },
        "create_own_folder": True,
        "utranslation_style": "flash_lfq_style_1",
        "input_uftypes": {
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.proteomics.THERMO_RAW: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.proteomics.converter.PYIOHAT_CSV: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.proteomics.validator.PEPTIDEFOREST_CSV: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.exp_design.output.PX_METADATA_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.quantification.FLASHLFQ_PSM_TSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.proteomics.quantification.FLASHLFQ_PEPTIDE_TSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.proteomics.quantification.FLASHLFQ_PROTEIN_TSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.proteomics.quantification.FLASHLFQ_BAYESFC_TSV: {
                "min": 0,
                "max": 1,
            },
        },
        # https://github.com/smith-chem-wisc/FlashLFQ/issues/99 found a version workoing with dotnet 5 here
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "CMD.dll",
                    "urn": "platform_independent/arc_independent/flash_lfq_1_2_3.zip",
                    "urn_md5": "0e340059479cab0e732e7ea2dd6b2aa7",
                    "external_md5": "5705a28abc075e45bbe1788edad85332",
                    "external_url": "https://github.com/smith-chem-wisc/FlashLFQ/releases/download/1.2.3/FlashLFQ.zip",
                },
            },
        },
        "citation": """
        Millikin, R. J., Solntsev, S. K., Shortreed, M. R., & Smith, L. M. (2017). Ultrafast Peptide Label-Free Quantification with FlashLFQ.
        In Journal of Proteome Research (Vol. 17, Issue 1, pp. 386-391). American Chemical Society (ACS). https://doi.org/10.1021/acs.jproteome.7b00608
        """,
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize flash_lfq_1_2_3 class."""
        super().__init__(*args, **kwargs)
