"""Urgap Plotly visualizer wrapper."""

import urgap


class PlotlyVisualizer(urgap.unode.UNodeBase):
    """Urgap wrapper for Plotly Express visualizations.

    Creates interactive HTML visualizations from CSV files using Plotly Express.
    """

    META_INFO = {
        "name": "PlotlyVisualizer",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "1.0.0", "exe_path": "Plotly/1_0_0/plotly_visualizer.py"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.any.CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.plotter.PLOTLY_HTML: {
                "min": 1,
                "max": 1,
            },
        },
        "engine": None,
        "engine_type": ("plotter",),
        "citation": "Urgap team 2025",
        "parameter_examples": """
            {
                "--plot-type": "scatter",  # scatter, bar, line, histogram, box, violin, heatmap
                "--x-column": "x_values",  # Column for x-axis
                "--y-column": "y_values",  # Column for y-axis
                "--color-column": "category",  # Optional: Column for color grouping
                "--title": "My Plot",  # Optional: Plot title
            }
        """,
    }

    def __init__(self) -> None:
        """Initialize PlotlyVisualizer."""
        super().__init__()

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for PlotlyVisualizer wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = ["python", str(self.exe_path)]
        utrace.urun_dict.command_list.extend(
            ["--csv-file", str(utrace.input_files[0].path)],
        )
        utrace.urun_dict.command_list.extend(
            ["--output-file", str(utrace.output_files[0].path)],
        )
        for parameter_key, parameter_value in utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ].items():
            if isinstance(parameter_value, list):
                for item in parameter_value:
                    utrace.urun_dict.command_list.extend([parameter_key, str(item)])
            else:
                utrace.urun_dict.command_list.extend(
                    [parameter_key, str(parameter_value)],
                )
        return utrace
