"""Urgap pymx_correct_instrument_drift_1_0_0 wrapper. Part of the MX GSK pipeline."""

import pandas as pd

import urgap


class pymx_correct_instrument_drift_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_correct_instrument_drift_1_0_0 resource.

    This wrapper calls the main resource to perform instrument drift correction.
    """

    META_INFO = {
        "name": "pymx_correct_instrument_drift_1_0_0",
        "version": "1.0.0",
        "release_date": "31.08.2022",
        "api_port": 42309,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "correct_instrument_drift_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_correct_instrument_drift_1_0_0.zip",
                    "urn_md5": "4124ad20084c6c42a658f7ecc03d043f",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/correct_instrument_drift_1_0_0.py",
                    "external_md5": "3eda104f87528ea04f2cbda8e2005cee",
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
            urgap.uftypes.ms.RUN_BATCH_META_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.mx.METADATA_MAP_JSON: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.exp_design.output.UTMX_METADATA_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.IONS_DRIFT_CORRECTED_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "correct_instrument_drift_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_correct_instrument_drift_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_correct_instrument_drift_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
             utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        # input files
        self.ions_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.IONS_CSV,
        )[0]

        self.experimental_design_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.exp_design.output.UTMX_METADATA_CSV,
        )[0]

        # Modify the experimental design input, as standardized design contains a
        # 'filename' column, which is not accepted by the underlying resource!
        self.experimental_design_tmp_file = (
            self.experimental_design_file.parent / "experimental_design_tmp_file.csv"
        )
        tmp_exp_design_df = pd.read_csv(
            self.experimental_design_file,
            usecols=lambda x: x not in ["filename", "bio_rep", "tech_rep"],
        )
        tmp_exp_design_df.to_csv(self.experimental_design_tmp_file, index=False)
        # append to tmp_files, so it will be removed after execution
        self.tmp_files.append(self.experimental_design_tmp_file)

        metadata_mapping_list_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.METADATA_MAP_JSON,
        )
        self.run_md_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.RUN_BATCH_META_CSV,
        )[0]

        # output files
        self.ions_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.IONS_DRIFT_CORRECTED_CSV,
        )[0]

        self.fraction_detected_ions = utrace.urun_dict.translations["all_params"][
            "fraction_detected_ions"
        ]["translated_value"]
        self.min_number_detected_ions = utrace.urun_dict.translations["all_params"][
            "min_number_detected_ions"
        ]["translated_value"]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-ions_i",
            str(self.ions_file),
            "-smdi",
            str(self.experimental_design_tmp_file),
            "-rmdi",
            str(self.run_md_file),
            "-ions_o",
            str(self.ions_output_file),
            "-mcif",
            str(self.fraction_detected_ions),
            "-mci",
            str(self.min_number_detected_ions),
        ]

        if metadata_mapping_list_file:
            utrace.urun_dict.command_list.extend(
                ["-mml", metadata_mapping_list_file[0]],
            )

        return utrace
