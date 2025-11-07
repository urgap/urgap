"""Urgap pymx_isotopologue_envelope_matching_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap


class pymx_isotopologue_envelope_matching_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_isotopologue_envelope_matching_1_0_0 resource.

    This wrapper calls the main resource to validate annotations based on
    isotopologue envelope matching.
    """

    META_INFO = {
        "name": "pymx_isotopologue_envelope_matching_1_0_0",
        "version": "1.0.0",
        "release_date": "30.06.2022",
        "api_port": 42311,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "isotopologue_envelope_matching_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_isotopologue_envelope_matching_1_0_0.zip",
                    "urn_md5": "dcf00cf16362ba1348a52849e0822bda",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/isotopologue_envelope_matching_1_0_0.py",
                    "external_md5": "e64e15f1415a453166a4bf93a32125a9",
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
            urgap.uftypes.ms.ANNOTATED_MET_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.mx.ADDUCTS_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.ANNOTATED_MET_IEM_CSV: {"min": 1, "max": 1},
            urgap.uftypes.ms.IONS_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "isotopologue_envelope_matching_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_isotopologue_envelope_matching_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_isotopologue_envelope_matching_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
             utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.pre_annotation_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ION_CHARGE_STATE_CSV,
        )[0]
        self.annotated_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ANNOTATED_MET_CSV,
        )[0]
        self.adducts_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.ADDUCTS_CSV,
        )[0]

        self.iem_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ANNOTATED_MET_IEM_CSV,
        )[0]
        self.ions_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.IONS_CSV,
        )[0]

        self.absolute_mass_tolerance = utrace.urun_dict.translations["all_params"][
            "absolute_mass_tolerance"
        ]["translated_value"]
        self.min_number_of_matched_isotopologues = utrace.urun_dict.translations[
            "all_params"
        ]["min_number_of_matched_isotopologues"]["translated_value"]
        self.remove_charge_mismatches = utrace.urun_dict.translations["all_params"][
            "remove_charge_mismatches"
        ]["translated_value"]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-pre_ann_i",
            str(self.pre_annotation_file),
            "-ann_i",
            str(self.annotated_file),
            "-ai",
            str(self.adducts_file),
            "-iem_o",
            str(self.iem_output_file),
            "-ions_o",
            str(self.ions_output_file),
            "-abs_tol",
            str(self.absolute_mass_tolerance),
            "-min_iso",
            str(self.min_number_of_matched_isotopologues),
        ]
        if self.remove_charge_mismatches is True:
            utrace.urun_dict.command_list.append("-rcm")

        return utrace
