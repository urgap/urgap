"""Urgap pymx_avg_files_dbscan_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap


class pymx_avg_files_dbscan_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_avg_files_dbscan_1_0_0 resource.

    This wrapper calls the main resource to avg and stitch together peaks following a
    multi-file alignment.
    """

    META_INFO = {
        "name": "pymx_avg_files_dbscan_1_0_0",
        "version": "1.0.0",
        "release_date": "05.05.2022",
        "api_port": 42305,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "avg_files_dbscan_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_avg_files_dbscan_1_0_0.zip",
                    "urn_md5": "6b71a0750094b99b0af580d490106135",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/avg_files_dbscan_1_0_0.py",
                    "external_md5": "c3babdc8d3b8cf85e8add8bd0458b764",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ["pymx"],
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.MULTI_ALIGN_SCANS_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.MULTI_AVG_SCANS_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "avg_files_dbscan_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_avg_files_dbscan_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_avg_files_dbscan_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.MULTI_ALIGN_SCANS_CSV,
        )[0]
        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.MULTI_AVG_SCANS_CSV,
        )[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(self.input_file),
            "-o",
            str(self.output_file),
        ]

        return utrace
