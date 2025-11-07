"""Urgap pymx_assign_analysis_batch_by_runtime_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap


class pymx_assign_analysis_batch_by_runtime_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_assign_analysis_batch_by_runtime_1_0_0 resource.

    This wrapper calls the main resource to extract peak information from an input
    mzml file.
    """

    META_INFO = {
        "name": "pymx_assign_analysis_batch_by_runtime_1_0_0",
        "version": "1.0.0",
        "release_date": "01.08.2022",
        "api_port": 42304,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "assign_analysis_batch_by_runtime_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_assign_analysis_batch_by_runtime_1_0_0.zip",
                    "urn_md5": "484ac8eb4760052a4841ab6e811610f9",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/assign_analysis_batch_by_runtime_1_0_0.py",
                    "external_md5": "33908c2b815cc0acfc3a2efeac7c8df7",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ["pymx"],
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.RUN_META_CSV: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.exp_design.output.UTMX_METADATA_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.RUN_BATCH_META_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "assign_analysis_batch_by_runtime_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_assign_analysis_batch_by_runtime_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_assign_analysis_batch_by_runtime_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        rmd_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.RUN_META_CSV,
        )
        metadata_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.exp_design.output.UTMX_METADATA_CSV,
        )[0]

        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.RUN_BATCH_META_CSV,
        )[0]

        batch_separation_time_factor = utrace.urun_dict.translations["all_params"][
            "batch_separation_time_factor"
        ]["translated_value"]
        time_format = utrace.urun_dict.translations["all_params"]["time_format"][
            "translated_value"
        ]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            *[str(file) for file in rmd_files],
            "-mdi",
            str(metadata_file),
            "-o",
            str(output_file),
            "-nm",
            str(batch_separation_time_factor),
            "-tf",
            str(time_format),
        ]

        return utrace
