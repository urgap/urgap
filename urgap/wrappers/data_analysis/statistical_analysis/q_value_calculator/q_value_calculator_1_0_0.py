"""Urgap q_value_calulator_1_0_0 wrapper."""

import urgap


class q_value_calculator_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the q_value_calculator_1_0_0 resource.

    This wrapper calls the main resource to compute PSM q-values
    on pyProtista output files.
    """

    META_INFO = {
        "name": "q_value_calculator_1_0_0",
        "version": "1.0.0",
        "release_date": "01.09.2022",
        "api_port": 42003,
        "engine_type": ("stats",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "q_value_calculator_1_0_0.py",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.any.CSV: {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.any.CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "q_value_calculator_style_1",
        "citation": "Urgap team (2022)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize q_value_calculator_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for q_value_calculator_1_0_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        input_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.any.CSV,
        )
        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.any.CSV,
        )[0]
        initial_engine = utrace.urun_dict.translations["all_params"]["initial_engine"][
            "translated_value"
        ]
        score_col = utrace.urun_dict.translations["all_params"][
            "validation_score_field"
        ]["translated_value"][initial_engine]
        bigger_scores_better = utrace.urun_dict.translations["all_params"][
            "bigger_scores_better"
        ]["translated_value"][initial_engine]

        concat_input_file = input_files[0].parent / "concated_input.csv"

        with open(concat_input_file, "w") as fout:
            for i, input_file in enumerate(input_files):
                fin = open(input_file)
                for j, line in enumerate(fin):
                    if i != 0 and j == 0:
                        continue
                    fout.write(line)
                fin.close()

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(concat_input_file),
            "-o",
            str(output_file),
            "-ie",
            str(initial_engine),
            "-sc",
            str(score_col),
        ]

        if bigger_scores_better is True:
            utrace.urun_dict.command_list.append("-bsb")
        return utrace
