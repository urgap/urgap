"""Urgap pymx_avg_scans_dbscan_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap


class pymx_avg_scans_dbscan_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the avg_scans_dbscan_1_0_0 resource.

    This wrapper calls the main resource to avg and stitch together peaks following a
    scan range alignment from an individual spectrum file.
    """

    META_INFO = {
        "name": "pymx_avg_scans_dbscan_1_0_0",
        "version": "1.0.0",
        "release_date": "05.05.2022",
        "api_port": 42306,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "avg_scans_dbscan_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_avg_scans_dbscan_1_0_0.zip",
                    "urn_md5": "eee51cac93baaf52c2a6d34c42aaa661",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/avg_scans_dbscan_1_0_0.py",
                    "external_md5": "afae54171a5a9fb250eea2f2bf72ec2b",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ["pymx"],
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.ALIGN_SCANS_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.AVG_SCANS_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "avg_scans_dbscan_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_avg_scans_dbscan_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_avg_scans_dbscan_1_0_0 wrapper.

        Prepares the cmd to execute with the avg_scans_dbscan_1_0_0 resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ALIGN_SCANS_CSV,
        )[0]

        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.AVG_SCANS_CSV,
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
