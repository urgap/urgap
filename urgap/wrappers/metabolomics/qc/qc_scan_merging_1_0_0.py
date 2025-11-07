"""Urgap qc_scan_merging_1_0_0 wrapper. Part of the MX QC suite."""

import urgap


class qc_scan_merging_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the qc_scan_merging_1_0_0 resource.

    This wrapper calls the main resource to create an interactive plotly plot for
    the general stage 2 QC - raw peaks, vs aligned vs recalibrated.
    """

    META_INFO = {
        "name": "qc_scan_merging_1_0_0",
        "version": "1.0.0",
        "release_date": "05.05.2022",
        "api_port": 42323,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "qc_scan_merging_1_0_0.py",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.SCANS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.ALIGN_SCANS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.AVG_SCANS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.RECAL_MZ_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.mx.QC_HTML: {"min": 1, "max": 1},
        },
        "utranslation_style": "mx_qc_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize qc_scan_merging_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for qc_scan_merging_1_0_0 wrapper.

        Prepares the cmd to execute with the qc_scan_merging_1_0_0 resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.scans_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SCANS_CSV,
        )[0]
        self.aligned_scans_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ALIGN_SCANS_CSV,
        )[0]
        self.avg_scans_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.AVG_SCANS_CSV,
        )[0]
        self.recal_scans_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.RECAL_MZ_CSV,
        )[0]
        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.QC_HTML,
        )[0]
        self.ion_mode = utrace.urun_dict.translations["all_params"]["ion_mode"][
            "translated_value"
        ]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-si",
            str(self.scans_file),
            "-sai",
            str(self.aligned_scans_file),
            "-savgi",
            str(self.avg_scans_file),
            "-sri",
            str(self.recal_scans_file),
            "-o",
            str(self.output_file),
            "-pol",
            str(self.ion_mode),
        ]
        return utrace
