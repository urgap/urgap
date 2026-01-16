"""Urgap determine_offset_1_0_0 wrapper."""

import urgap


class determine_offset_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the determine_offset_1_0_0 resource.

    This wrapper calls the main resource to compute machine offsets in ppm
    on filtered pyProtista output files.
    """

    META_INFO = {
        "name": "determine_offset_1_0_0",
        "version": "1.0.0",
        "release_date": "01.09.2022",
        "api_port": 42722,
        "engine_type": ("converter", "proteomics"),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "determine_offset_1_0_0.py",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.any.CSV: {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.qc.OFFSET_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "determine_offset_style_1",
        "citation": "Urgap team (2022)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize determine_offset_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for determine_offset_1_0_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "--output",
            str(utrace.output_files[0].path),
            "--pd_query",
            utrace.urun_dict.translations["all_params"]["pandas_query_string"][
                "translated_value"
            ],
            "--input_files",
        ]
        for input_file in utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.any.CSV,
        ):
            utrace.urun_dict.command_list.append(str(input_file))
        return utrace
