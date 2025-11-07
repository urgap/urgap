"""Urgap qc_global_mz_recalibration_1_0_0 wrapper. Part of the MX QC suite."""

import urgap


class qc_global_mz_recalibration_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the qc_global_mz_recalibration_1_0_0 resource.

    This wrapper calls the main resource to create an interactive plotly plot for
    the global mz recalibration.
    """

    META_INFO = {
        "name": "qc_global_mz_recalibration_1_0_0",
        "version": "1.0.0",
        "release_date": "08.09.2022",
        "api_port": 42319,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "qc_global_mz_recalibration_1_0_0.py",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.GLOBAL_RECAL_MZ_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.mx.BEST_ION_MET_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.mx.INSTRUMENT_RESOLUTION_CSV: {
                "min": 0,
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
        """Initialize qc_global_mz_recalibration_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for qc_global_mz_recalibration_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.recal_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.GLOBAL_RECAL_MZ_CSV,
        )[0]
        self.best_ion_met_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.BEST_ION_MET_CSV,
        )[0]

        instr_res_path_ls = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.INSTRUMENT_RESOLUTION_CSV,
        )
        if len(instr_res_path_ls) != 0:
            self.instr_res_file = instr_res_path_ls[0]
        else:
            self.instr_res_file = None

        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.QC_HTML,
        )[0]

        self.ms1_resolution = utrace.urun_dict.translations["all_params"][
            "ms1_resolution"
        ]["translated_value"]
        self.annotation_accuracy = utrace.urun_dict.translations["all_params"][
            "annotation_accuracy"
        ]["translated_value"]
        self.instrument = utrace.urun_dict.translations["all_params"]["instrument"][
            "translated_value"
        ]
        self.absolute_mass_tolerance = utrace.urun_dict.translations["all_params"][
            "absolute_mass_tolerance"
        ]["translated_value"]
        self.ppm_mass_tolerance = utrace.urun_dict.translations["all_params"][
            "ppm_mass_tolerance"
        ]["translated_value"]
        self.accuracy_range = utrace.urun_dict.translations["all_params"][
            "accuracy_range"
        ]["translated_value"]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-bimi",
            str(self.best_ion_met_file),
            "-ri",
            str(self.recal_file),
            "-iri",
            str(self.instr_res_file),
            "-o",
            str(self.output_file),
            "-res",
            str(self.ms1_resolution),
            "-acc",
            str(self.annotation_accuracy),
            "-instr",
            str(self.instrument),
            "-abs_tol",
            str(self.absolute_mass_tolerance),
            "-ppm_tol",
            str(self.ppm_mass_tolerance),
        ]
        for mzb in self.accuracy_range:
            utrace.urun_dict.command_list.extend(["-mzb", mzb])

        return utrace
