
import pandas as pd




    Allows to filter and merge multiple csv files based on a pandas query string.
    """

    META_INFO = {
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
                "min": 1,
                "max": -1,
        },
        "output_uftypes": {
                "min": 1,
                "max": 1,
            },
        },
        "engine": None,
        "engine_type": ("io",),
    }


    def preflight(
        self,

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        for file in utrace.input_files:
            utrace.urun_dict.command_list.extend(["-i", str(file.path)])

        utrace.urun_dict.command_list.extend(
            [
                "-o",
                str(utrace.output_files[0].path),
        )
        for parameter_key, parameter_value in utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ].items():
            if parameter_value is not None:

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

        data = []
        wrapper_version = "{major}.{minor}.{patch}".format(
        )

            fig.add_trace(
                go.Violin(
                    name=col,
                    box_visible=True,
                    meanline_visible=True,
            )
        first_wrapper_section = {
            "section_title": f"CSV stats for node {cls.META_INFO['name']}",
            "section_text": f"Wrapper version {wrapper_version}. Release data {cls.META_INFO['release_date']}",
            "tables": [
                {
                    "title": "Data Sample",
                    "caption": "",
                },
                {
                    "title": "Data description",
                },
            ],
            "figures": [
                {
                    "title": "Useless Violin Plot :)",
                    "data": offline.plot(
                    ),
                    "_type": "html",
                    "caption": "Just a demo ...",
            ],
        }

        data.append(first_wrapper_section)
        return data