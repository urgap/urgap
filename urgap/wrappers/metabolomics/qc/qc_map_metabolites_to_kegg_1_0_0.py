"""Urgap qc_map_metabolites_to_kegg_1_0_0 wrapper. Part of the MX QC suite."""

import logging

import pandas as pd

import urgap


class qc_map_metabolites_to_kegg_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the qc_map_metabolites_to_kegg_1_0_0 resource.

    This wrapper calls the main resource to create an interactive svg map of the KEGG
    pathway including quantitative data on annotated metabolites.
    """

    META_INFO = {
        "name": "qc_map_metabolites_to_kegg_1_0_0",
        "version": "1.0.0",
        "release_date": "27.09.2022",
        "api_port": 42321,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "qc_map_metabolites_to_kegg_1_0_0.py",
                },
            },
        },
        "input_uftypes": {
            # TODO: should the KEGG map be provided, or always downloaded - uparma param? By whom - wrapper, or resource?
            urgap.uftypes.ms.KEGG_MAP_HTML: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.ANNOTATED_MET_IEM_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            # TODO: also include QC_PNG, but that with changes on kegg2svg!
            urgap.uftypes.mx.QC_SVG: {"min": 1, "max": 1},
        },
        "utranslation_style": "mx_qc_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize qc_map_metabolites_to_kegg_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ):
        """Preflight routine for qc_map_metabolites_to_kegg_1_0_0 wrapper.

        Args:
             utrace: Combination of urun_dict, ufile_list and unode.meta.
        """
        annotated_met_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ANNOTATED_MET_IEM_CSV,
        )[0]

        df = pd.read_csv(annotated_met_file)
        df = df[["KEGG_ID", "ion_intensity_median", "Metabolite_name_HMDB"]]
        df = df.rename(
            columns={
                "KEGG_ID": "ID",
                "ion_intensity_median": "value",
                "Metabolite_name_HMDB": "name",
            },
        )
        df = df[df["ID"].notna()]
        df["ID"] = df["ID"].str.lstrip("cpd:")

        self.quant_file = f"{annotated_met_file.parent}/quant_file.csv"
        df.to_csv(self.quant_file, index=False)

    def execute(
        self,
        utrace: urgap.UTrace,
    ):
        """Execute routine for qc_map_metabolites_to_kegg_1_0_0 wrapper.

        Executes the main function of the qc_map_metabolites_to_kegg_1_0_0 resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
        """
        kegg_map_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.KEGG_MAP_HTML,
        )[0]
        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.QC_SVG,
        )[0]

        main = self.import_engine_as_python_function()

        main(
            kegg_html=kegg_map_file,
            output_filename=output_file,
            quant_file=self.quant_file,
        )

        logging.info("DONE!")
