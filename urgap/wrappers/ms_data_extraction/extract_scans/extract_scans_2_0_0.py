"""Urgap extract_scans_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap

from urgap.wrappers.ms_data_extraction.extract_scans.extract_scans_1_0_0 import (
    extract_scans_1_0_0 as xscans,
)


class extract_scans_2_0_0(xscans):
    """Urgap wrapper for the extract_scans_2_0_0 resource.

    This wrapper calls the main resource to extract peak information from an input
    mzml file.
    """

    META_INFO = {
        "name": "extract_scans_2_0_0",
        "version": "1.0.1",
        "release_date": "06.10.2022",
        "api_port": 42502,
        "engine_type": (
            "data_extractor",
            "ms",
        ),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 1},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "extract_scans_2_0_0.py",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML: {
                "min": 0,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.SCANS_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "extract_scans_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize extract_scans_2_0_0 class."""
        super().__init__(*args, **kwargs)

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight."""
        lineage_roots = utrace.input_files[0].lineage_root_files
        assert len(lineage_roots) == 1

        urgap.ucore.set_column_value(
            utrace.output_files[0].path,
            "filename",
            lineage_roots[0],
        )
        return utrace
