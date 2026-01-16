"""Urgap VennDiagram_1_1_0 wrapper."""

import csv
import logging

import pandas as pd

import urgap


class venndiagram_1_1_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the VennDiagram_1_1_0 resource.

    This wrapper calls the main resource to plot a venn diagramm for a list of .csv
    result files (2-5). Exports the umap figure as SVG, as well as underlying data
    as CSV.
    """

    META_INFO = {
        "name": "venndiagram_1_1_0",
        "version": "1.1.0",
        "release_date": "06.04.2022",
        "api_port": 42601,
        "engine_type": ("plotter",),
        "wrapper_version": {
            "major": 1,
            "minor": 1,
            "patch": 0,
        },
        "platform_independent": True,
        # The executable for platform independent is expected to be under
        # $URGAP_HOME/resources/platform_independent/arc_independent/VennDiagram_1_1_0/
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "venndiagram_1_1_0.py",
                    # "zip_md5": "<>",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.any.CSV: {
                "min": 2,
                "max": 5,
            },
        },
        "output_uftypes": {
            urgap.uftypes.plotter.VENN_RESULTS_SVG: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.plotter.VENN_RESULTS_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "venndiagram_style_1",
        "citation": "Kremer, L. P. M., Leufken, J., Oyunchimeg, P., Schulze, S. & Fufezan, C. (2016) Proteome res. 15, 788-794",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize VennDiagram_1_1_0 class."""
        super().__init__(*args, **kwargs)

    def execute(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Execute routine for VennDiagram_1_1_0 wrapper.

        Reads in the provided dataframes from the input files and pipes them further
        into the main funtion of the resource. Following execution, during which the
        SVG plot is created and underlying data is returned, the grouped data is saved
        as CSV file.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        venndiagram_main = self.import_engine_as_python_function()
        data_list = []
        feature_col_list = utrace.urun_dict.translations["all_params"][
            "feature_columns"
        ]["translated_value"]
        if isinstance(feature_col_list, str):
            feature_col_list = [feature_col_list]
        msg = f"Plotting Venn diagram {utrace.output_files[0].object_name} using feature columns {feature_col_list}"
        logging.info(msg)
        for ufile in utrace.input_files:
            venn_data = {"label": ufile.object_name, "data": set()}
            with open(ufile.path) as icsv:
                for ldict in csv.DictReader(icsv):
                    identity = []
                    for feature_col in feature_col_list:
                        identity.append(ldict.get(feature_col, ""))
                    venn_data["data"].add(" ".join(identity))
            data_list.append(venn_data)
        return_dict = venndiagram_main(
            data=data_list,
            output_file=utrace.output_files.get_path_objects_by_uftype(
                urgap.uftypes.any.SVG,
            )[0],
        )
        data = []
        for k in return_dict:
            if k == "input":
                continue
            data.append(
                pd.Series(name=k, data=True, index=list(return_dict[k]["results"])),
            )

        df = pd.concat(data, axis=1, keys=[s.name for s in data])
        df = df.fillna(False)
        df.to_csv(
            utrace.output_files.get_path_objects_by_uftype(
                urgap.uftypes.plotter.VENN_RESULTS_CSV,
            )[0],
        )
        return utrace
