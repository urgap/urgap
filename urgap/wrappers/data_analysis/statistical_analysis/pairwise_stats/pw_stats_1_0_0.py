"""Urgap pw_stats_1_0_0 wrapper."""

import logging

import urgap


class pw_stats_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pw_stats_1_0_0 search engine.

    This wrapper calls the main resource to calculate pairwise statistics on hits,
    e.g. peptide following identification/quantification. Using statsmodels it
    performs a limma like analysis, known from R. Multitesting is applied to correct
    the p-value calculation.
    """

    META_INFO = {
        "name": "pw_stats_1_0_0",
        "version": "1.0.0",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 1},
        "release_date": "14.10.2021",
        "api_port": 42002,
        "engine_type": ("stats",),
        "platform_independent": True,
        "utranslation_style": "pw-stats_style_1",
        "engine": {
            "platform_independent": {"arc_independent": {"exe": "pw_stats_1_0_0.py"}},
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.quantification.FLASHLFQ_PSM_TSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.exp_design.output.PX_METADATA_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.stats.PWSTATS_CSV: {"min": 1, "max": 1},
        },
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize pw_stats_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pw_stats_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        # Handle the input file and format it into a merged quant_exp_design tmp file
        # to be provided to the resource
        quant_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.quantification.FLASHLFQ_PSM_TSV,
        )[0]
        exp_design_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.exp_design.output.PX_METADATA_CSV,
        )[0]

        # Handle the output file
        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.stats.PWSTATS_CSV,
        )[0]

        comp_list = utrace.urun_dict.translations["all_params"]["comparisons_list"][
            "translated_value"
        ]
        index_columns = utrace.urun_dict.translations["all_params"]["index_columns"][
            "translated_value"
        ]
        feature_columns = utrace.urun_dict.translations["all_params"][
            "feature_columns"
        ]["translated_value"]

        if len(feature_columns) != 1:
            logging.error(
                f"The pw-stats node only works with one feature column. E.g. "
                f"either quant value, intensity. You provided {feature_columns}!",
            )
            raise ValueError
        feature_column = feature_columns[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(quant_file),
            "-edi",
            str(exp_design_file),
            "-o",
            str(output_file),
            "-cm",
            str(
                utrace.urun_dict.translations["all_params"]["pval_correction_method"][
                    "translated_value"
                ],
            ),
            "-cl",
            *comp_list,
            "-ic",
            *index_columns,
            "-fc",
            feature_column,
        ]
        return utrace
