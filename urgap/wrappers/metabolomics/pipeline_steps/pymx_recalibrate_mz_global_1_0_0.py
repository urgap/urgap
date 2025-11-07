"""Urgap pymx_recalibrate_mz_global_1_0_0 wrapper. Part of the MX GSK pipeline."""

import logging

import urgap


class pymx_recalibrate_mz_global_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_recalibrate_mz_global_1_0_0 resource.

    This wrapper calls the main resource to recalibrate the mz value based on adducts,
    ref masses and calibrators using a polynomial fit to account for multiple
    reference masses.
    """

    META_INFO = {
        "name": "pymx_recalibrate_mz_global_1_0_0",
        "version": "1.0.0",
        "release_date": "05.05.2022",
        "api_port": 42316,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "recalibrate_mz_global_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_recalibrate_mz_global_1_0_0.zip",
                    "urn_md5": "7974591885ccb371ae47d9b753a448ff",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/recalibrate_mz_global_1_0_0.py",
                    "external_md5": "ee69b5aa61318ba18aff4c801eb4d900",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ["pymx"],
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.MULTI_AVG_SCANS_CSV: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.ms.MERGED_IONS_CSV: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.mx.ADDUCTS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.mx.MASS_SHIFT_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.mx.CAL_MASS_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.GLOBAL_RECAL_MZ_CSV: {"min": 1, "max": 1},
            urgap.uftypes.mx.BEST_ION_MET_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "recalibrate_mz_global_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_recalibrate_mz_global_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Execute routine for pymx_recalibrate_mz_global_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_files_ls = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.MULTI_AVG_SCANS_CSV,
        )
        self.input_files_ls.extend(
            utrace.input_files.get_path_objects_by_uftype(
                urgap.uftypes.ms.MERGED_IONS_CSV,
            ),
        )

        if len(self.input_files_ls) > 1:
            logging.error(
                f"You can only provide either {urgap.uftypes.ms.MULTI_AVG_SCANS_CSV} "
                f"or {urgap.uftypes.ms.MERGED_IONS_CSV} to the node. "
                f"NOT both simultaneously!",
            )
            raise ValueError

        self.adducts_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.ADDUCTS_CSV,
        )[0]
        self.mass_shift_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.MASS_SHIFT_CSV,
        )[0]
        self.cal_mass_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.CAL_MASS_CSV,
        )[0]
        self.global_recal_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.GLOBAL_RECAL_MZ_CSV,
        )[0]
        self.best_ion_met_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.BEST_ION_MET_CSV,
        )[0]
        self.ion_mode = utrace.urun_dict.translations["all_params"]["ion_mode"][
            "translated_value"
        ]
        self.absolute_mass_tolerance = utrace.urun_dict.translations["all_params"][
            "absolute_mass_tolerance"
        ]["translated_value"]
        self.ppm_mass_tolerance = utrace.urun_dict.translations["all_params"][
            "ppm_mass_tolerance"
        ]["translated_value"]
        self.minimum_intensity = utrace.urun_dict.translations["all_params"][
            "minimum_intensity"
        ]["translated_value"]
        self.degrees_of_freedom = utrace.urun_dict.translations["all_params"][
            "degrees_of_freedom"
        ]["translated_value"]
        self.adduct_confidence = utrace.urun_dict.translations["all_params"][
            "adduct_confidence"
        ]["translated_value"]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(self.input_files_ls[0]),
            "-ai",
            str(self.adducts_file),
            "-msi",
            str(self.mass_shift_file),
            "-cmi",
            str(self.cal_mass_file),
            "-ro",
            str(self.global_recal_output_file),
            "-bimo",
            str(self.best_ion_met_file),
            "-pol",
            str(self.ion_mode),
            "-abs_tol",
            str(self.absolute_mass_tolerance),
            "-ppm_tol",
            str(self.ppm_mass_tolerance),
            "-mi",
            str(self.minimum_intensity),
            "-pd",
            str(self.degrees_of_freedom),
            "-cl",
            *self.adduct_confidence,
        ]

        return utrace
