"""Urgap filter_csv_1_0_0 wrapper."""

import logging

import pandas as pd

import urgap


class filter_csv_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the filter_csv_1_0_0 resource.

    Allows to filter and merge multiple csv files based on a pandas query string.
    """

    META_INFO = {
        "name": "filter_csv_1_0_0",
        "version": "1.0.0",
        "release_date": "20.02.2020",
        "api_port": 42206,
        "engine_type": ("io",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "filter_csv_1_0_0.py",
                },
            },
        },
        "utranslation_style": "csv_filter_style_1",
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
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize filter_csv_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for filter_csv_1_0_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        logging.info("[ -ENGINE- ] Executing filtering process ..")

        utrace.urun_dict.command_list = ["python", str(self.exe_path)]
        for file in utrace.input_files:
            utrace.urun_dict.command_list.extend(["-i", str(file.path)])

        utrace.urun_dict.command_list.extend(
            [
                "-o",
                str(utrace.output_files[0].path),
                "-q",
                str(
                    utrace.urun_dict.translations["all_params"]["pandas_query_string"][
                        "translated_value"
                    ],
                ),
            ],
        )

        return utrace

    @classmethod
    def generate_wrapper_vis(cls, ufile: urgap.UFile) -> list:
        """Generate basic nodes specific data visualization.

        Args:
            ufile (urgap.UFile): UFile object containing node execution data.

        Returns:
            list of urgap.<TBD_VIS_LIST_CLASS>: _description_
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

        df = pd.read_csv(ufile.path)
        df_describe = df.describe().reset_index()
        data = []
        wrapper_version = "{major}.{minor}.{patch}".format(
            **cls.META_INFO["wrapper_version"],
        )
        n = min(10, df.shape[0])

        fig = go.Figure()  # TODO: generate urgap dashboard, layout=layout)
        for col in df.columns:
            fig.add_trace(
                go.Violin(
                    # x=df[col],
                    y=df[col],
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
                    "headers": list(df.columns),
                    "rows": df.sample(n).to_dict("records"),
                    "caption": "",
                },
                {
                    "title": "Data description",
                    "headers": list(df_describe.columns),
                    "rows": df_describe.to_dict("records"),
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
