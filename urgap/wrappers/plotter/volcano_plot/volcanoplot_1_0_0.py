"""Urgap volcanoplot_1_0_0 wrapper."""

import logging

import urgap


class volcanoplot_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the volcanoplot_1_0_0 resource.

    This wrapper calls the main resource to generate a volcano plot figure on data
    post-statistical analysis, where the log2 FC and pvalues are provided.
    """

    META_INFO = {
        "name": "volcanoplot_1_0_0",
        "version": "1.0.0",
        "release_date": "21.10.2021",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "api_port": 42602,
        "engine_type": ("plotter",),
        "platform_independent": True,
        "utranslation_style": "volcano_style_1",
        "engine": {
            "platform_independent": {
                "arc_independent": {"exe": "volcanoplot_1_0_0.py"},
            },
        },
        "input_uftypes": {
            urgap.uftypes.stats.PWSTATS_CSV: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.plotter.VOLCANO_PDF: {"min": 1, "max": 1},
        },
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize volcanoplot_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for volcanoplot_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.stats.PWSTATS_CSV,
        )[0]
        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.plotter.VOLCANO_PDF,
        )[0]

        logging.info("[ -ENGINE- ] Creating VolcanoPlots ..")

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(input_file),
            "-o",
            str(output_file),
            "-pval_t",
            str(
                utrace.urun_dict.translations["all_params"][
                    "pvalue_significance_threshold"
                ]["translated_value"],
            ),
            "-fc_t",
            str(
                utrace.urun_dict.translations["all_params"][
                    "log2_foldchange_threshold"
                ]["translated_value"],
            ),
        ]
        if (
            utrace.urun_dict.translations["all_params"]["use_pvalue_adj"][
                "translated_value"
            ]
            is True
        ):
            utrace.urun_dict.command_list.append("-adj")

        return utrace
