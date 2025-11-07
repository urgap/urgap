"""Urgap filter_parquet_1_0_0 wrapper."""

import logging

import urgap


class filter_parquet_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the filter_parquet_1_0_0 resource.

    Allows to filter and merge multiple parquet files based on a pandas query string.
    """

    META_INFO = {
        "name": "filter_parquet_1_0_0",
        "version": "1.0.0",
        "release_date": "20.02.2020",
        "api_port": 42207,
        "engine_type": ("io",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "filter_parquet_1_0_0.py",
                },
            },
        },
        "utranslation_style": "parquet_filter_style_1",
        "input_uftypes": {
            urgap.uftypes.any.PARQUET: {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.any.PARQUET: {
                "min": 1,
                "max": 1,
            },
        },
        "citation": "Urgap team (2024)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize filter_parquet_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for filter_parquet_1_0_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        logging.info("[ -ENGINE- ] Executing filtering process ..")

        utrace.urun_dict.command_list = ["python", str(self.exe_path)]
        for file in utrace.input_files:
            utrace.urun_dict.command_list.extend(["-i", str(file.path)])

        utrace.urun_dict.command_list.extend(
            [
                "-o",
                str(utrace.output_files[0].path),
            ],
        )
        query = utrace.urun_dict.translations["all_params"]["pandas_query_string"][
            "translated_value"
        ]
        if query is not None:
            (utrace.urun_dict.command_list.extend(["-q", query]),)
        return utrace
