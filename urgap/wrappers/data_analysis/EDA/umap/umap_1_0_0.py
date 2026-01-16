"""Urgap umap_1_0_0 wrapper."""

import urgap


class umap_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the umap_1_0_0 resource.

    This wrapper calls the main resource to create a umap on any statistical data
    using the umap package. Exports the umap figure as PDF, as well as underlying data
    as CSV. See publication provided under META_INFO["citation"] for further info
    about UMAP.
    """

    META_INFO = {
        "name": "umap_1_0_0",
        "version": "1.0.0",
        "release_date": "04.04.22",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "api_port": 42001,
        "engine_type": ("plotter",),
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "umap_1_0_0.py",
                    # "zip_md5": "<>",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "umap-learn",
                    "unimod-mapper",
                ],
            },
        },
        "input_uftypes": {
            urgap.uftypes.stats.ANY: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.stats.UMAP_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.plotter.UMAP_PDF: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "umap_style_1",
        "citation": """
        McInnes, L., Healy, J., & Melville, J. (2018). UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction (Version 3).
        arXiv. https://doi.org/10.48550/ARXIV.1802.03426
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize umap_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for umap_1_0_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.stats.ANY,
        )[0]
        output_pdf = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.plotter.UMAP_PDF,
        )[0]
        output_csv = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.stats.UMAP_CSV,
        )[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "--input",
            str(input_file),
            "--output_pdf",
            str(output_pdf),
            "--output_csv",
            str(output_csv),
            "--n_components",
            str(
                utrace.urun_dict.translations["all_params"]["cluster_n_components"][
                    "translated_value"
                ],
            ),
            "--min_distance",
            str(
                utrace.urun_dict.translations["all_params"]["cluster_min_distance"][
                    "translated_value"
                ],
            ),
            "--metric",
            str(
                utrace.urun_dict.translations["all_params"]["cluster_distance_metric"][
                    "translated_value"
                ],
            ),
            "--n_neighbours",
            str(
                utrace.urun_dict.translations["all_params"]["cluster_n_neighbours"][
                    "translated_value"
                ],
            ),
            "--index_columns",
        ]
        for ic in utrace.urun_dict.translations["all_params"]["index_columns"][
            "translated_value"
        ]:
            utrace.urun_dict.command_list.append(ic)
        utrace.urun_dict.command_list.append("--feature_columns")
        for fc in utrace.urun_dict.translations["all_params"]["feature_columns"][
            "translated_value"
        ]:
            utrace.urun_dict.command_list.append(fc)
        utrace.urun_dict.command_list.append("--marker_columns")
        for mc in utrace.urun_dict.translations["all_params"]["marker_columns"][
            "translated_value"
        ]:
            utrace.urun_dict.command_list.append(mc)
        utrace.urun_dict.command_list.append("--colour_columns")
        for cc in utrace.urun_dict.translations["all_params"]["colour_columns"][
            "translated_value"
        ]:
            utrace.urun_dict.command_list.append(cc)

        return utrace
