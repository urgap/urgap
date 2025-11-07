"""Urgap qc_instrument_drift_correction_1_0_0 wrapper. Part of the MX QC suite."""

import json
import logging

import pandas as pd

import urgap


class qc_instrument_drift_correction_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the qc_instrument_drift_correction_1_0_0.py resource.

    This wrapper calls the main resource to create an interactive plotly plot for
    the instrument drift correction.
    """

    META_INFO = {
        "name": "qc_instrument_drift_correction_1_0_0",
        "version": "1.0.0",
        "release_date": "08.09.2022",
        "api_port": 42320,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "qc_instrument_drift_correction_1_0_0.py",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.IONS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.IONS_DRIFT_CORRECTED_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.RUN_BATCH_META_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.mx.METADATA_MAP_JSON: {
                "min": 0,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.mx.QC_PDF: {"min": 1, "max": 1},
        },
        "utranslation_style": "mx_qc_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize qc_instrument_drift_correction_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for correct_instrument_drift_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. In addition, generates and
        combines the metadata file. Subsequently, assembles the command_list, which is
        executed during execute().

        Args:
             utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        # Deal with sample metadata
        sample_md_df = create_experimental_design(utrace)

        # append mapping exp design to the urun_dict_exp_design if available
        # Check if a METADATA_MAP_JSON file was provided to the node
        metadata_mapping_file_list = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.METADATA_MAP_JSON,
        )
        # if not provided, the list would be empty and only original metadata would be
        # provided to the resource
        if len(metadata_mapping_file_list) != 0:
            with open(metadata_mapping_file_list[0]) as file:
                merged_metadata_list = json.load(file)
            merged_metadata_df = self.format_metadata_mapping_list(merged_metadata_list)
            sample_md_df = pd.concat([sample_md_df, merged_metadata_df])

        # 2. Deal with run metadata
        run_md_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.RUN_BATCH_META_CSV,
        )[0]
        run_md_df = pd.read_csv(run_md_file)

        # Merge sample and run metadata to provide to the node!
        if (
            pd.Series(run_md_df["run_id"])
            .sort_values(ignore_index=True)
            .equals(sample_md_df["filename"].sort_values(ignore_index=True))
        ):
            full_md_df = pd.merge(
                sample_md_df,
                run_md_df[["run_id", "start_time", "analysis_batch"]],
                left_on="filename",
                right_on="run_id",
            )
            full_md_df = full_md_df.drop("run_id", axis=1)
        else:
            missing_md_info = [
                filename
                for filename in run_md_df["run_id"].to_list()
                if filename not in sample_md_df["filename"].to_list()
            ]
            logging.error(
                f"Your run metadata contains information about samples, to which sample"
                f"metadata is missing. The following samples are affected: "
                f"{','.join(missing_md_info)}. Check your inputs! ",
            )
            raise ValueError

        # Write out to tmp file to  to the resource
        self.full_md_tmp_file = (
            utrace.output_files[0].path.parent / "full_metadata_tmp_file.csv"
        )
        full_md_df.to_csv(self.full_md_tmp_file, index=False)

        # append to tmp_files, so it will be removed after execution
        self.tmp_files.append(self.full_md_tmp_file)

        # Define the input files
        self.ions_input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.IONS_CSV,
        )[0]
        self.drift_corrected_ions_input_file = (
            utrace.input_files.get_path_objects_by_uftype(
                urgap.uftypes.ms.IONS_DRIFT_CORRECTED_CSV,
            )[0]
        )

        # Define the output files
        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.QC_PDF,
        )[0]

        # Generate the command list
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(self.ions_input_file),
            "-ci",
            str(self.drift_corrected_ions_input_file),
            "-mdi",
            str(self.full_md_tmp_file),
            "-o",
            str(self.output_file),
        ]

        return utrace

    # TODO: this function is again used in multiple nodes!
    def format_metadata_mapping_list(self, merged_metadata_list: list) -> pd.DataFrame:
        """Format a loaded external metadata mapping json.

        The function iterates over the loaded list of dicts, translates the dict keys
        into node style and returns the metadata in dataframe format.

        Args:
            merged_metadata_list: List of dicts containing sample metadata.

        Returns:
            Dataframe containing merged experimental design.
        """
        translated_merged_metadata_list = []
        for entry in merged_metadata_list:
            translated_entry = urgap.instances.uparma.translate(
                param_dict=entry,
                original_style=urgap.instances.uparma.original_style,
                translated_style=self.META_INFO["utranslation_style"],
            )
            formatted_translated_entry = {}
            for _key, _dict in translated_entry.items():
                formatted_translated_entry.update(
                    {_dict["translated_key"]: _dict["translated_value"]},
                )
            translated_merged_metadata_list.append(formatted_translated_entry)
        merged_metadata_df = pd.DataFrame(translated_merged_metadata_list)

        return merged_metadata_df


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
