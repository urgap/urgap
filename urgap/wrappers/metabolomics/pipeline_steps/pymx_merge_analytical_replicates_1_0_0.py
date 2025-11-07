"""Urgap pymx_merge_analytical_replicates_1_0_0 wrapper. Part of the MX GSK pipeline."""

import pandas as pd

import urgap


class pymx_merge_analytical_replicates_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the merge_analytical_replicates_1_0_0 resource.

    This wrapper calls the main resource to filter the annotation and ions tables based on input parameters.
    """

    META_INFO = {
        "name": "pymx_merge_analytical_replicates_1_0_0",
        "version": "1.0.0",
        "release_date": "08.08.2022",
        "api_port": 42312,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "merge_analytical_replicates_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_merge_analytical_replicates_1_0_0.zip",
                    "urn_md5": "a6b439066e5e51273b2bf8230a537fd8",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/merge_analytical_replicates_1_0_0.py",
                    "external_md5": "479e402af37a7f3fdc2c7c9a83c3fdcf",
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
            urgap.uftypes.ms.RUN_BATCH_META_CSV: {"min": 1, "max": 1},
            urgap.uftypes.exp_design.output.UTMX_METADATA_CSV: {
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
            urgap.uftypes.ms.RUN_BATCH_META_CSV: {"min": 1, "max": 1},
            urgap.uftypes.mx.METADATA_MAP_JSON: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "merge_analytical_replicates_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_merge_analytical_replicates_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_merge_analytical_replicates_1_0_0 wrapper.

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
        self.annotation_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ANNOTATED_MET_IEM_CSV,
        )[0]
        self.rmd_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.RUN_BATCH_META_CSV,
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

        # output files
        self.ions_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.IONS_CSV,
        )[0]
        self.annotation_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ANNOTATED_MET_IEM_CSV,
        )[0]
        self.rmd_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.RUN_BATCH_META_CSV,
        )[0]
        self.experimental_design_map_file = (
            utrace.output_files.get_path_objects_by_uftype(
                urgap.uftypes.mx.METADATA_MAP_JSON,
            )[0]
        )

        self.delimiter = utrace.urun_dict.translations["all_params"]["delimiter"][
            "translated_value"
        ]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-ions_i",
            str(self.ions_file),
            "-ann_i",
            str(self.annotation_file),
            "-ri",
            str(self.rmd_file),
            "-edi",
            str(self.experimental_design_tmp_file),
            "-ions_o",
            str(self.ions_output_file),
            "-ann_o",
            str(self.annotation_output_file),
            "-ro",
            str(self.rmd_output_file),
            "-edmo",
            str(self.experimental_design_map_file),
            "-del",
            str(self.delimiter),
        ]

        return utrace
