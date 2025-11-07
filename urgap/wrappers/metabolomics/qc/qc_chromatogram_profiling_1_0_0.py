"""Urgap qc_chromatogram_profiling_1_0_0 wrapper. Part of the MX QC suite."""

import pandas as pd

import urgap


class qc_chromatogram_profiling_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the qc_chromatogram_profiling_1_0_0 resource.

    This wrapper calls the main resource to create an interactive plotly plot for
    chromatogram profiling.
    """

    META_INFO = {
        "name": "qc_chromatogram_profiling_1_0_0",
        "version": "1.0.0",
        "release_date": "08.09.2022",
        "api_port": 42318,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "qc_chromatogram_profiling_1_0_0.py",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.SPECTRA_META_CSV: {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.mx.QC_HTML: {"min": 1, "max": 1},
        },
        "utranslation_style": "mx_qc_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize qc_chromatogram_profiling_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Execute routine for qc_chromatogram_profiling_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. In addition, generates and
        combines the metadata file. Subsequently, assembles the command_list, which is
        executed during execute().

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_file_list = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SPECTRA_META_CSV,
        )
        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.QC_HTML,
        )[0]

        experimental_design = create_experimental_design(utrace)

        # Write out to tmp file to  to the resource
        self.experimental_design_tmp_file = (
            utrace.output_files[0].path.parent / "experimental_design_tmp_file.csv"
        )
        experimental_design.to_csv(self.experimental_design_tmp_file, index=False)

        # append to tmp_files, so it will be removed after execution
        self.tmp_files.append(self.experimental_design_tmp_file)

        # Generate the command list
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-edi",
            str(self.experimental_design_tmp_file),
            "-o",
            str(self.output_file),
        ]
        for file in self.input_file_list:
            utrace.urun_dict.command_list.extend(["-i", str(file)])

        return utrace


# TODO: this function will live in a global space to be available for many nodes, which actually use it!
def create_experimental_design(
    utrace: urgap.UTrace,
) -> pd.DataFrame:
    """Transform the exp-setup param of the urun_dict into a pandas DataFrame.

    Args:
        utrace: Combination of urun_dict, ufile_list and unode.meta.

    Returns:
        Dataframe containing experimental design.
    """
    experimental_design_list = utrace.urun_dict.translations["all_params"][
        "experiment_setup"
    ]["translated_value"]
    rows = []
    for data in experimental_design_list:
        dict_out = {}
        for _key, dict in data.items():
            dict_out.update({dict["translated_key"]: dict["translated_value"]})
        rows.append(dict_out)
    experimental_design_df = pd.DataFrame(rows)
    experimental_design_df = experimental_design_df.sort_values(
        by="filename",
        ignore_index=True,
    )
    return experimental_design_df
