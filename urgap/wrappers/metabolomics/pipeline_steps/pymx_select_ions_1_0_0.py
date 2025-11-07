"""Urgap pymx_select_ions_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap


class pymx_select_ions_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_select_ions_1_0_0 resource.

    This wrapper calls the main resource to filter the annotation and ions tables based on input parameters.
    """

    META_INFO = {
        "name": "pymx_select_ions_1_0_0",
        "version": "1.0.0",
        "release_date": "27.07.2022",
        "api_port": 42317,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "select_ions_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_select_ions_1_0_0.zip",
                    "urn_md5": "ccb472af33cd813f7927fde3412f4fad",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/select_ions_1_0_0.py",
                    "external_md5": "f294715faa08eb27371d175a32c786ac",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ["pymx"],
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.IONS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.ANNOTATED_MET_IEM_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.IONS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.ANNOTATED_MET_IEM_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "select_ions_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_select_ions_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_select_ions_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
             utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.ions_input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.IONS_CSV,
        )[0]
        self.annotation_input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ANNOTATED_MET_IEM_CSV,
        )[0]

        self.ions_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.IONS_CSV,
        )[0]

        self.annotation_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ANNOTATED_MET_IEM_CSV,
        )[0]

        self.min_percentage_detected_ions = utrace.urun_dict.translations["all_params"][
            "min_percentage_detected_ions"
        ]["translated_value"]
        self.correlation_threshold = utrace.urun_dict.translations["all_params"][
            "correlation_threshold"
        ]["translated_value"]
        self.scan_threshold = utrace.urun_dict.translations["all_params"][
            "scan_threshold"
        ]["translated_value"]
        self.keep_non_annotated_metabolites = utrace.urun_dict.translations[
            "all_params"
        ]["keep_non_annotated_metabolites"]["translated_value"]
        self.keep_uncharged_ions = utrace.urun_dict.translations["all_params"][
            "keep_uncharged_ions"
        ]["translated_value"]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-ions_i",
            str(self.ions_input_file),
            "-ann_i",
            str(self.annotation_input_file),
            "-ions_o",
            str(self.ions_output_file),
            "-ann_o",
            str(self.annotation_output_file),
            "-dt",
            str(self.min_percentage_detected_ions),
            "-tt",
            str(self.correlation_threshold),
            "-st",
            str(self.scan_threshold),
        ]
        if self.keep_non_annotated_metabolites is True:
            utrace.urun_dict.command_list.append("-knam")
        if self.keep_uncharged_ions is True:
            utrace.urun_dict.command_list.append("-kui")

        return utrace
