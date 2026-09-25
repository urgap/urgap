"""Urgap FilterTabularToCSV wrapper."""

import urgap


class FilterTabularToCSV(urgap.unode.UNodeBase):
    """Urgap wrapper for the filter_csv resource.

    Allows to filter and merge multiple csv files based on a polars query string.
    """

    META_INFO = {
        "name": "FilterTabularToCSV",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "1.0.0", "exe_path": "FilterTabular/1_0_0/filter_tabular.py"},
            {"version": "2.0.0", "exe_path": "FilterTabular/2_0_0/filter_tabular.py"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.any.TABULAR: {
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
        "engine": None,
        "engine_type": ("io",),
        "citation": "Urgap team (2021)",
        "parameter_examples": """
            These are possible unode_execution_parameters for FilterTabularToCSV.

            -q: Use polars query string

            For example:
            {
                "-q": "your_filter_expression_here"
            }

            Polars SQL expression syntax:
            {
                "-q": "500 < exp_mz AND exp_mz < 1000"
            }

            Common examples:
            {"-q": "charge == 2"}
            {"-q": "charge == 2 AND accuracy_ppm < 5"}
            {"-q": "1000 < exp_mz AND exp_mz < 2000"}

            REMEMBER: Always use "-q" as the key, NOT "query", NOT "q", ONLY "-q"
        """,
    }

    def __init__(self) -> None:
        """Initialize FilterTabularToCSV class."""
        super().__init__()

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for FilterTabularToCSV wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = ["python", str(self.exe_path), "-m", "csv"]
        for file in utrace.input_files:
            utrace.urun_dict.command_list.extend(["-i", str(file.path)])

        utrace.urun_dict.command_list.extend(
            [
                "-o",
                str(utrace.output_files[0].path),
            ],
        )
        for parameter_key, parameter_value in utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ].items():
            if parameter_value is not None:
                utrace.urun_dict.command_list.extend([parameter_key, parameter_value])

        return utrace

    @classmethod
    def generate_wrapper_vis(cls, ufile: urgap.UFile) -> list:
        """Generate basic nodes specific data visualization.

        Args:
            ufile (urgap.UFile): UFile object

        Returns:
            list of urgap.<TBD_VIS_LIST_CLASS>: FilterTabularToCSV information.
            format similar to
            data = [
                {
                    "section_title": "",
                    "section_text": "",
                    "networks": [
                        {
                            "title": "",
                            "links": "",
                            "caption" :"".
                        }
                    ]
                    "figures": [
                        {
                            "title": "",
                            "data": "",
                            "_type": "html|img",
                            "caption": "",
                        }
                    ],
                    "tables": [
                        {
                            "title": "",
                            "headers": "",
                            "rows": [],
                            "caption":""
                        }
                    ],
                }
            ]
            potentially pydantic or similar
        """
        import pandas as pd
        import plotly.graph_objs as go

        from plotly import offline

        input_csv_df = pd.read_csv(ufile.path)
        describe_df = input_csv_df.describe().reset_index()
        data = []
        wrapper_version = "{major}.{minor}.{patch}".format(
            **cls.META_INFO["wrapper_version"],
        )
        n = min(10, input_csv_df.shape[0])

        fig = go.Figure()
        for col in input_csv_df.columns:
            fig.add_trace(
                go.Violin(
                    y=input_csv_df[col],
                    name=col,
                    box_visible=True,
                    meanline_visible=True,
                ),
            )
        first_wrapper_section = {
            "section_title": f"CSV stats for node {cls.META_INFO['name']}",
            "section_text": f"Wrapper version {wrapper_version}. Release data {cls.META_INFO['release_date']}",
            "tables": [
                {
                    "title": "Data Sample",
                    "headers": list(input_csv_df.columns),
                    "rows": input_csv_df.sample(n).to_dict("records"),
                    "caption": "",
                },
                {
                    "title": "Data description",
                    "headers": list(describe_df.columns),
                    "rows": describe_df.to_dict("records"),
                },
            ],
            "figures": [
                {
                    "title": "Useless Violin Plot :)",
                    "data": offline.plot(
                        fig,
                        include_plotlyjs=False,
                        output_type="div",
                    ),
                    "_type": "html",
                    "caption": "Just a demo ...",
                },
            ],
        }

        data.append(first_wrapper_section)
        return data
