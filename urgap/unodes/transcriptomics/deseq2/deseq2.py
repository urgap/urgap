"""Urgap DESeq2 wrapper."""

import pandas as pd

import urgap


class DESeq2(urgap.unode.UNodeBase):
    """Urgap wrapper for the DESeq2.

    Allows to calculate differential expression.
    """

    META_INFO = {
        "name": "DESeq2",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "1.0.0", "exe_path": "DESeq2/1_0_0/deseq2.py"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.any.CSV: {
                "min": 2,
                "max": 2,
            },
        },
        "output_uftypes": {
            urgap.uftypes.any.CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "engine": None,
        "engine_type": ("io",),
        "citation": "Urgap team (2021)",
        "parameter_examples": """

            -q: Use pandas query string

            For example:

            {
                "-q": "`padj` < 0.05"
            }

        """,
    }

    def __init__(self) -> None:
        """Initialize DESeq2 class."""
        super().__init__()

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for DESeq2 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = ["python", str(self.exe_path)]
        for file in utrace.input_files:
            utrace.urun_dict.command_list.extend(["-i", str(file.path)])

        utrace.urun_dict.command_list.extend(
            [
                "-o",
                str(utrace.output_files[0].path),
            ],
        )
        for parameter_key, parameter_value in utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ].items():
            if parameter_value is not None:
                utrace.urun_dict.command_list.extend([parameter_key, parameter_value])
        return utrace
