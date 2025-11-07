"""Urgap pymx_annotate_metabolites_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap


class pymx_annotate_metabolites_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the align_files_dbscan_1_0_0 resource.

    This wrapper calls the main resource to annotate the identified peaks to known
    metabolites represented in the loaded metabolites DB (usually HMDB).
    """

    META_INFO = {
        "name": "pymx_annotate_metabolites_1_0_0",
        "version": "1.0.0",
        "release_date": "30.06.2022",
        "api_port": 42303,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "annotate_metabolites_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_annotate_metabolites_1_0_0.zip",
                    "urn_md5": "3a3d330b0d20e911a2458ca24e68b625",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/annotate_metabolites_1_0_0.py",
                    "external_md5": "3d8da8b452613c84af3f19638cb3f2fa",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ["pymx"],
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.ION_CHARGE_STATE_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.mx.ANNOTATION_MET_HDF5: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.mx.ANNOTATION_MET_EXCLUSION_CSV: {
                "min": 1,
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
            urgap.uftypes.mx.INSTRUMENT_RESOLUTION_CSV: {
                "min": 0,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.ANNOTATED_MET_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "annotate_metabolites_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_annotate_metabolites_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_annotate_metabolites_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
             utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ION_CHARGE_STATE_CSV,
        )[0]
        self.annotation_db_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.ANNOTATION_MET_HDF5,
        )[0]
        self.exclusion_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.ANNOTATION_MET_EXCLUSION_CSV,
        )[0]
        self.adducts_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.ADDUCTS_CSV,
        )[0]
        self.mass_shift_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.MASS_SHIFT_CSV,
        )[0]
        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ANNOTATED_MET_CSV,
        )[0]
        instr_res_file_ls = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.INSTRUMENT_RESOLUTION_CSV,
        )
        if len(instr_res_file_ls) != 0:
            self.instr_res_file = instr_res_file_ls[0]
        else:
            self.instr_res_file = None

        self.instrument = utrace.urun_dict.translations["all_params"]["instrument"][
            "translated_value"
        ]
        self.ms1_resolution = utrace.urun_dict.translations["all_params"][
            "ms1_resolution"
        ]["translated_value"]
        self.extraction_polarity = utrace.urun_dict.translations["all_params"][
            "extraction_polarity"
        ]["translated_value"]
        self.ion_mode = utrace.urun_dict.translations["all_params"]["ion_mode"][
            "translated_value"
        ]
        self.annotation_accuracy = utrace.urun_dict.translations["all_params"][
            "annotation_accuracy"
        ]["translated_value"]
        self.absolute_mass_tolerance = utrace.urun_dict.translations["all_params"][
            "absolute_mass_tolerance"
        ]["translated_value"]
        self.ppm_mass_tolerance = utrace.urun_dict.translations["all_params"][
            "ppm_mass_tolerance"
        ]["translated_value"]
        self.remove_charge_mismatches = utrace.urun_dict.translations["all_params"][
            "remove_charge_mismatches"
        ]["translated_value"]
        self.adduct_confidence = utrace.urun_dict.translations["all_params"][
            "adduct_confidence"
        ]["translated_value"]
        self.accuracy_range = utrace.urun_dict.translations["all_params"][
            "accuracy_range"
        ]["translated_value"]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(self.input_file),
            "-met_db",
            str(self.annotation_db_file),
            "-ei",
            str(self.exclusion_file),
            "-ai",
            str(self.adducts_file),
            "-msi",
            str(self.mass_shift_file),
            "-iri",
            str(self.instr_res_file),
            "-o",
            str(self.output_file),
            "-instr",
            str(self.instrument),
            "-res",
            str(self.ms1_resolution),
            "-met_pol",
            str(self.extraction_polarity),
            "-pol",
            str(self.ion_mode),
            "-acc",
            str(self.annotation_accuracy),
            "-abs_tol",
            str(self.absolute_mass_tolerance),
            "-ppm_tol",
            str(self.ppm_mass_tolerance),
            "-cl",
            *self.adduct_confidence,
            "-mzb",
            *self.accuracy_range,
        ]
        if self.remove_charge_mismatches is True:
            utrace.urun_dict.command_list.append("-rcm")

        return utrace
