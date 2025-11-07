"""Urgap filter_fcs_1_0_1 wrapper."""

import urgap


class filter_fcs_1_0_1(urgap.unode.UNodeBase):
    """Urgap wrapper for the filter_fcs_1_0_1 resource.

    Allows to filter and merge multiple FCS files based on a pandas query string.
    """

    META_INFO = {
        "name": "filter_fcs_1_0_1",
        "version": "1.0.1",
        "release_date": "18.07.2023",
        "api_port": 42110,
        "engine_type": ("flow_cytometry", "io"),
        "wrapper_version": {"major": 1, "minor": 1, "patch": 0},
        "platform_independent": True,
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "filter_fcs_1_0_1.py",
                },
            },
        },
        "utranslation_style": "fcs_filter_style_1",
        "input_uftypes": {
            urgap.uftypes.flow_cytometry.FCS: {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.flow_cytometry.FCS: {
                "min": 1,
                "max": 1,
            },
        },
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize filter_fcs_1_0_1 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for filter_fcs_1_0_1 wrapper.

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
                "-q",
                str(
                    utrace.urun_dict.translations["all_params"]["pandas_query_string"][
                        "translated_value"
                    ],
                ),
            ],
        )

        return utrace
