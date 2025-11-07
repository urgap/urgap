"""Urgap qc_sample_merging_1_0_0 wrapper. Part of the MX QC suite."""

import logging

import urgap


class qc_sample_merging_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the sample_merging_qc_1_0_0 resource.

    This wrapper calls the main resource to create an interactive plotly plot for
    the sample merging QC - raw peaks, vs globally aligned vs globally recalibrated.
    """

    META_INFO = {
        "name": "qc_sample_merging_1_0_0",
        "version": "1.0.0",
        "release_date": "08.09.2022",
        "api_port": 42322,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "qc_sample_merging_1_0_0.py",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.AVG_SCANS_CSV: {
                "min": 0,
                "max": -1,
            },
            urgap.uftypes.ms.RECAL_MZ_CSV: {
                "min": 0,
                "max": -1,
            },
            urgap.uftypes.ms.MULTI_ALIGN_SCANS_CSV: {"min": 1, "max": 1},
            urgap.uftypes.ms.GLOBAL_RECAL_MZ_CSV: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.mx.QC_HTML: {"min": 1, "max": 1},
        },
        "utranslation_style": "mx_qc_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize qc_sample_merging_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for qc_sample_merging_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        avg_files_ls = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.AVG_SCANS_CSV,
        )

        recal_files_ls = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.RECAL_MZ_CSV,
        )

        if len(avg_files_ls) != 0 and len(recal_files_ls) != 0:
            logging.error(
                f"You provided {len(avg_files_ls)} aligned files and "
                f"{len(recal_files_ls)} recalibrated aligned file. This node"
                f" cannot scope for both recalibrated and not calibrated data "
                f"of the same origin!",
            )
            raise OSError

        self.input_file_list = avg_files_ls + recal_files_ls
        self.aligned_samples_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.MULTI_ALIGN_SCANS_CSV,
        )[0]
        self.recal_samples_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.GLOBAL_RECAL_MZ_CSV,
        )[0]

        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.QC_HTML,
        )[0]

        self.ion_mode = utrace.urun_dict.translations["all_params"]["ion_mode"][
            "translated_value"
        ]

        utrace.urun_dict.command_list = ["python", str(self.exe_path)]
        for file in self.input_file_list:
            utrace.urun_dict.command_list.extend(["-i", str(file)])
        utrace.urun_dict.command_list.extend(
            [
                "-ai",
                str(self.aligned_samples_file),
                "-ri",
                str(self.recal_samples_file),
                "-o",
                str(self.output_file),
                "-pol",
                str(self.ion_mode),
            ],
        )

        return utrace
