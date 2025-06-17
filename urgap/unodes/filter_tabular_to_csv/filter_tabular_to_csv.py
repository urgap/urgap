
import pandas as pd




    Allows to filter and merge multiple csv files based on a pandas query string.
    """

    META_INFO = {
        "name": "FilterTabularToCSV",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "1.0.0", "exe_path": "FilterTabular/1_0_0/filter_tabular.py"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
                "min": 1,
                "max": 1,
            },
        },
        "engine": None,
        "engine_type": ("io",),
    }

    def __init__(self) -> None:
        """Initialize FilterTabularToCSV class."""
        super().__init__()

    def preflight(
        self,
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
        """Generate basic nodes specific data visualization.

        Args:

        Returns:
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