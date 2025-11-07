"""Urgap extract_scans_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap


class extract_scans_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the extract_scans_1_0_0 resource.

    This wrapper calls the main resource to extract peak information from an input
    mzml file.
    """

    META_INFO = {
        "name": "extract_scans_1_0_0",
        "version": "1.0.0",
        "release_date": "27.04.2022",
        "api_port": 42501,
        "engine_type": (
            "data_extractor",
            "ms",
        ),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "deprecated": True,
        "is_replaced_by": "extract_scans_3_0_0, which is using the resources from the simepy package",
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "extract_scans_1_0_0.py",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML: {
                "min": 0,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.SCANS_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "extract_scans_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize calculate_ion_charge_state_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for extract_scans_1_0_0 wrapper.

        Prepares the cmd to execute with the extract_scans_1_0_0 resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        mzml_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML,
        )[0]
        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SCANS_CSV,
        )[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(mzml_file),
            "-o",
            str(output_file),
        ]
        return utrace

    @classmethod
    def generate_wrapper_vis(cls, ufile: urgap.UFile) -> list:
        """Generate basic nodes specific data visualization.

        Args:
            ufile (urgap.UFile):

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
        import numpy as np
        import pandas as pd
        import plotly.graph_objs as go

        from plotly import offline

        # TODO: these params will be refactored to have it unified for both ion modes
        #  as well as instrument types!
        POLARITY = "negative"
        INSTR = "Thermo"

        if POLARITY == "negative":
            peak_name = ["Pyruvate", "Isocitrate", "TCA", "PFTD"]
            mz_theor = [87.008769, 191.0197262, 514.284374, 712.9472642]
            if INSTR == "Thermo":
                mz_range = [
                    [87.005, 87.015],
                    [191.005, 191.04],
                    [514.225, 514.375],
                    [712.85, 713.1],
                ]
            elif INSTR == "Bruker":
                mz_range = [
                    [87.000, 87.04],
                    [191.005, 191.055],
                    [514.225, 514.375],
                    [712.875, 713.1],
                ]
        elif POLARITY == "positive":
            mz_range = [
                [90.052, 90.062],
                [203.215, 203.240],
                [538.23, 538.38],
                [664.05, 664.23],
            ]
            mz_theor = [90.054978473, 203.223046852, 538.280891, 664.116394]
            peak_name = ["L-Alanine", "Spermine", "TCA", "NAD+"]

        fig_ls = []
        for i, _w in enumerate(mz_range):
            mz_th = mz_theor[i]
            pk_name = peak_name[i]
            delta_tol = 0.02  # don't plot obviously wrong hits

            # 1. Raw data

            df = pd.read_csv(ufile.path)

            mzmatch = []
            for j in range(len(df.spectrum_id.unique())):
                df_sub = df.loc[df["spectrum_id"] == j + 1]["mass"]
                de = df_sub - mz_th
                if min(abs(de)) <= delta_tol:
                    mz = df_sub[abs(de) == min(abs(de))].values[0]
                    mzmatch.append(mz)
                else:
                    mzmatch.append(np.nan)
            xseries = pd.Series(mzmatch)

            # Create the actual Figure

            fig = go.Figure()
            fig.add_trace(go.Histogram(x=xseries, nbinsx=20, name=pk_name))
            fig.add_vline(x=xseries.median(), line_width=3, line_dash="dash")
            fig.add_annotation(
                text=f"centroid s.d = {round(xseries.std(), 5)} <br> # scans = {xseries.shape[0]}",
                align="left",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.99,
                y=0.95,
            )
            fig.update_xaxes(showline=True, linewidth=2, linecolor="black", mirror=True)
            fig.update_yaxes(
                showline=True,
                linewidth=2,
                linecolor="black",
                mirror=True,
                showgrid=True,
                gridwidth=1,
                gridcolor="rgb(200,200,200)",
            )
            fig.update_layout(
                title=f"{pk_name} - raw centroids",
                title_x=0.5,
                xaxis_title="m/z",
                yaxis_title="Frequency",
                bargroupgap=0.01,
                paper_bgcolor="rgb(255,255,255)",
                plot_bgcolor="rgb(255,255,255)",
            )
            fig_ls.append(fig)

        # Assemble the dashboard
        data = []
        wrapper_version = "{major}.{minor}.{patch}".format(
            **cls.META_INFO["wrapper_version"],
        )
        first_wrapper_section = {
            "section_title": f"Stats for node {cls.META_INFO['name']}",
            "section_text": f"Wrapper version {wrapper_version}. Release data {cls.META_INFO['release_date']}",
            "figures": [
                {
                    "data": offline.plot(
                        fig_ls[0],
                        include_plotlyjs=False,
                        output_type="div",
                    ),
                    "_type": "html",
                },
                {
                    "data": offline.plot(
                        fig_ls[1],
                        include_plotlyjs=False,
                        output_type="div",
                    ),
                    "_type": "html",
                },
                {
                    "data": offline.plot(
                        fig_ls[2],
                        include_plotlyjs=False,
                        output_type="div",
                    ),
                    "_type": "html",
                },
                {
                    "data": offline.plot(
                        fig_ls[3],
                        include_plotlyjs=False,
                        output_type="div",
                    ),
                    "_type": "html",
                },
            ],
        }

        data.append(first_wrapper_section)
        return data
