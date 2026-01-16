"""Urgap percolator_3_5_0 wrapper."""

import contextlib
import os
import shutil

from collections.abc import Callable
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import pandas as pd

with contextlib.suppress(BaseException):
    from chemical_composition.chemical_composition_kb import PROTON

import urgap


class percolator_3_5_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the percolator_3_5_0 executable.

    Percolator uses a semi-supervised machine learning to discriminate correct from
    incorrect peptide-spectrum matches, and calculates accurate statistics such as
    q-value (FDR) and posterior error probabilities. See publication
    provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "percolator_3_5_0",
        "version": "3.5.0",
        "release_date": "19.04.2020",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "api_port": 42731,
        "engine_type": ("validation", "proteomics"),
        "platform_independent": False,
        "utranslation_style": "percolator_style_2",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "percolator",
                    "uri": None,
                    "urn": "darwin/arm64/percolator_3_5_0.zip",
                    "urn_md5": "8aab634972d4c4cc9010b53681baf37f",
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "percolator",
                    "uri": None,
                    "urn": "darwin/x86_64/percolator_3_5_0.zip",
                    "urn_md5": "8aab634972d4c4cc9010b53681baf37f",
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "linux": {
                "arm64": {
                    "exe": "percolator",
                    "uri": None,
                    "urn": "linux/arm64/percolator_3_5_0.zip",
                    "urn_md5": "106b0abbba163d9d5e6e1a512f130e9e",
                    # ^-- build by hand - if urgap.packaging system is used, then md5 cb1618ab855e69e80b2d32b4183b6a18
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "percolator",
                    "uri": None,
                    "urn": "linux/x86_64/percolator_3_5_0.zip",
                    "urn_md5": "106b0abbba163d9d5e6e1a512f130e9e",
                    # ^-- build by hand - if urgap.packaging system is used, then md5 cb1618ab855e69e80b2d32b4183b6a18
                    "external_md5": None,
                    "external_url": None,
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.converter.PYIOHAT_CSV: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.proteomics.FASTA: {
                "min": 0,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.validator.PERCOLATOR_CSV: {"min": 1, "max": 2},
        },
        "citation": """
        The, M., MacCoss, M. J., Noble, W. S., & Käll, L. (2016). Fast and Accurate Protein False Discovery Rates on Large-Scale Proteomics Data Sets with Percolator 3.0.
        In Journal of the American Society for Mass Spectrometry (Vol. 27, Issue 11, pp. 1719-1727). American Chemical Society (ACS). https://doi.org/10.1007/s13361-016-1460-7
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize percolator_3_5_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for percolator_3_5_0 wrapper.

        During preflight,
            - input file aligned with percolator style is formatted and created
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.output_type_dict = utrace.output_files.get_index_groups_by_uftypes()
        psm_file_indices = utrace.output_files.get_indices_by_uftype(
            urgap.uftypes.proteomics.validator.PERCOLATOR_CSV,
        )
        self.result_psms = (
            str(utrace.output_files[psm_file_indices[0]].path) + "targets_broken"
        )

        self.decoy_psms = (
            str(utrace.output_files[psm_file_indices[0]].path) + "decoys_broken"
        )

        input_tsv = self.create_input_file(utrace)
        utrace.urun_dict.command_list = [
            self.exe_path,
            "--only-psms",
            input_tsv,
            "--results-psms",
            self.result_psms,
            "--decoy-results-psms",
            self.decoy_psms,
        ]
        return self.create_command_list(utrace)

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for percolator_2_08 wrapper.

        During postflight the individual fixed and decoy dataframes coming from the
        percolator tool, are read and merged together before they are stored into the
        pre-defined urgap output file.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        fixed_targets_path = utrace.output_files[0].path.parent / Path(
            utrace.output_files[0].path.name + "_percolator_out_fixed.tsv",
        )

        fixed_decoys_path = utrace.output_files[0].path.parent / Path(
            utrace.output_files[0].path.name + "_percolator_out_fixed_decoys.tsv",
        )

        self.tmp_files.append(self.result_psms)
        self.tmp_files.append(self.decoy_psms)
        self.tmp_files.append(fixed_targets_path)
        self.tmp_files.append(fixed_decoys_path)

        for broken_path, fixed_path in [
            (self.decoy_psms, fixed_decoys_path),
            (self.result_psms, fixed_targets_path),
        ]:
            with open(str(broken_path)) as fin, open(str(fixed_path), "w") as fout:
                for i, line in enumerate(fin):
                    if i == 0:
                        fout.write(line)
                        continue
                    l = line.split("\t")[:5]
                    prot = " ".join(line.split("\t")[5:])
                    l.append(prot)
                    fout.write("\t".join(l))
        # rename files again

        output_decoys = pd.read_csv(fixed_decoys_path, sep="\t", index_col=False)
        output_decoys = output_decoys[["PSMId", "q-value", "posterior_error_prob"]]

        output_targets = pd.read_csv(fixed_targets_path, sep="\t", index_col=False)
        output_targets = output_targets[["PSMId", "q-value", "posterior_error_prob"]]

        qvals = pd.concat([output_targets, output_decoys])

        unified_df = pd.read_csv(self.merged_frame)

        final_df = pd.merge(
            unified_df,
            qvals,
            left_on="PSMId",
            right_on="PSMId",
            how="left",
        )
        final_df = final_df[~final_df["q-value"].isna()]
        idx = self.output_type_dict[".percolator.csv"][0]
        final_df.to_csv(utrace.output_files[idx].path)

        #  Part specific for only version 3.5.0
        if (
            self.META_INFO["version"] == "3.5.0"
            and (
                utrace.output_files[0].path.parent / "target_protein_qvals.tsv"
            ).exists()
        ):
            utrace.extend_output_files_by_uftype(
                urgap.uftypes.proteomics.validator.PERCOLATOR_CSV,
            )
            protein_targets = (
                utrace.output_files[0].path.parent / "target_protein_qvals.tsv"
            )
            protein_decoys = (
                utrace.output_files[0].path.parent / "decoy_protein_qvals.tsv"
            )
            targets = pd.read_csv(
                protein_targets,
                sep="\t",
            )
            decoys = pd.read_csv(
                protein_decoys,
                sep="\t",
            )
            self.tmp_files.extend([protein_decoys, protein_targets])
            td_df = pd.concat([targets, decoys]).sort_values("ProteinGroupId")
            output_path = utrace.output_files[1]
            td_df.to_csv(str(output_path.path), index=False)

        return utrace

    def create_command_list(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Create the command list to execute percolator executable.

        Based on the input parameters, the command list is created, which will be used
        during execute step to run percolator.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        for key, translated_dict in utrace.urun_dict.translations["all_params"].items():
            if key in [
                "bigger_scores_better",
                "validation_score_field",
                "delimiter",
                "enzyme",
                "database",
                "cpus",
            ]:
                continue
            # Part specific for only version 3.5.0
            if self.META_INFO["version"] == "3.5.0":
                if (
                    translated_dict["translated_value"] is True
                    and translated_dict["translated_key"] == "--picked-protein"
                ):
                    utrace.urun_dict.command_list.append(
                        translated_dict["translated_key"],
                    )
                    utrace.urun_dict.command_list.append(utrace.input_files[1].path)
                    # target+decoy protein q-val output files
                    target_proteins = (
                        utrace.output_files[0].path.parent / "target_protein_qvals.tsv"
                    )

                    decoy_proteins = (
                        utrace.output_files[0].path.parent / "decoy_protein_qvals.tsv"
                    )

                    utrace.urun_dict.command_list.append("-l")
                    utrace.urun_dict.command_list.append(f"{target_proteins}")
                    utrace.urun_dict.command_list.append("-L")
                    utrace.urun_dict.command_list.append(f"{decoy_proteins}")

            elif translated_dict["translated_value"] is True:
                utrace.urun_dict.command_list.append(translated_dict["translated_key"])
            elif (
                translated_dict["translated_value"] is False
                or translated_dict["translated_value"] is None
            ):
                continue
            elif translated_dict["original_key"] == "percolator_post_processing":
                utrace.urun_dict.command_list.append(
                    translated_dict["translated_value"],
                )
            else:
                utrace.urun_dict.command_list.append(translated_dict["translated_key"])
                utrace.urun_dict.command_list.append(
                    translated_dict["translated_value"],
                )
        return utrace

    def create_input_file(
        self,
        utrace: urgap.UTrace,
    ) -> os.PathLike:
        """Create the input file following percolator convention.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            Path to input file.
        """
        req_headers = ["PSMId", "Label", "ScanNr", "Peptide", "Proteins"]
        features = [
            "PSMId",
            "Label",
            "ScanNr",
            "lnrsp",
            "deltlcn",
            "deltcn",
            "score",  # Xcorr
            "sp",
            "mass",  # mass
            "peplen",  # peplen
            # "IonFrac",
            "charge_1",
            "charge_2",
            "charge_3",
            "charge_4",
            "charge_5",
            "charge_6",
            "charge_7",
            "charge_8",
            "charge_9",
            "charge_10",
            "enzn",
            "enzc",
            "enzint",
            "dm",
            "absdm",
            "Peptide",
            "Proteins",
        ]

        default_directions_features = dict.fromkeys(features, 0)
        default_directions_features.update(dict.fromkeys(req_headers, "-"))
        default_directions_features["PSMId"] = "DefaultDirection"

        delimiter = utrace.urun_dict.translations["all_params"]["delimiter"][
            "translated_value"
        ]

        unified_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.converter.PYIOHAT_CSV,
        )
        dfs = []
        for f in unified_files:
            _df = pd.read_csv(f)
            dfs.append(_df)
        df = pd.concat(dfs)

        old_columns = df.columns

        df = df.sort_values(["spectrum_id", "rank"])

        df.loc[df["is_decoy"] is True, "Label"] = "-1"
        df.loc[df["is_decoy"] is False, "Label"] = "1"

        # One hot encode charges
        df = pd.merge(
            df,
            pd.get_dummies(df.charge, prefix="charge"),
            left_index=True,
            right_index=True,
        )
        df = df.loc[1:]

        empty_charges = [
            f"charge_{i}" for i in range(11) if i not in df["charge"].unique()
        ]
        df.loc[:, empty_charges] = 0

        # Add Pep Len
        df["peplen"] = df["sequence"].str.len()

        # mass
        df["mass"] = (df["exp_mz"] * df["charge"]) - (df["charge"] - 1) * PROTON

        # add dm
        df["dm"] = df["ucalc_mz"] - df["exp_mz"]

        # absdm ???
        df["absdm"] = abs(df["dm"])

        if len(df["search_engine"].unique()) == 1:
            se = df["search_engine"].iloc[0]
        else:
            msg = "Multiple engines detected in dataframe. Percolator can only handle one search engine at a time."
            raise Exception(
                msg,
            )
        bigger_scores_better = utrace.urun_dict.translations["all_params"][
            "bigger_scores_better"
        ]["translated_value"][se]
        validate_score_field = utrace.urun_dict.translations["all_params"][
            "validation_score_field"
        ]["translated_value"][se]
        df["score"] = df[validate_score_field]
        if bigger_scores_better is False:
            df["score"] = -np.log10(df["score"])

        df["sp"] = df["score"].rank(method="max")
        df["lnrsp"] = np.log(df["sp"])

        def apply_parallel(df_grouped: pd.DataFrame, func: Callable, threads: int = -1) -> pd.DataFrame:
            """Execute a task in a parallel manner.

            Args:
                df_grouped (pd.DataFrame): grouped by dataframe to perform analysis on
                func (function) : function to be applied in parallel
                threads (int): number of threads to be used for parallelization

            Returns:
                pd.DataFrame following processing of input df with defined func
            """
            if threads == -1:
                threads = cpu_count()
            with Pool(threads) as p:
                ret_list = p.map(func, [group for name, group in df_grouped])
            return pd.concat(ret_list)

        threads = utrace.urun_dict.translations["all_params"]["cpus"][
            "translated_value"
        ]
        df = apply_parallel(
            df.groupby("spectrum_id"),
            self.delta_score,
            threads=threads,
        ).reset_index(drop=True)

        df["enzn"] = df["enzn"].astype(int)
        df["enzc"] = df["enzc"].astype(int)
        df["enzint"] = df["missed_cleavages"].astype(int)

        df["modifications"] = df["modifications"].fillna("")
        df.loc[df["modifications"] == "", "Peptide"] = (
            df["sequence_pre_aa"].str.split(delimiter).str[0]
            + "."
            + df["sequence"]
            + "."
            + df["sequence_post_aa"].str.split(delimiter).str[0]
        )
        df.loc[df["modifications"] != "", "Peptide"] = (
            df["sequence_pre_aa"].str.split(delimiter).str[0]
            + "."
            + df["sequence"]
            + "[#"
            + df["modifications"]
            + "]."
            + df["sequence_post_aa"].str.split(delimiter).str[0]
        )

        df["Proteins"] = df["protein_id"]
        df["ScanNr"] = df["spectrum_id"]

        df = df.reset_index()
        df = df.rename(columns={"index": "PSMId"})

        feature_df = df[features]
        fname = utrace.output_files[0].path.parent / "percolator_input.tsv"
        self.tmp_files.append(fname)
        feature_df = feature_df.sort_values("ScanNr")
        feature_df["Proteins"] = (
            feature_df["Proteins"].str.split(r"<\|>").str.join("\t")
        )

        feature_df.to_csv(
            fname,
            sep="\t",
            index=False,
        )
        self.remove_quotes(fname)

        _new = [*list(old_columns), "PSMId"]
        self.merged_frame = utrace.output_files[0].path.parent / "merge_frame.csv"
        self.tmp_files.append(self.merged_frame)
        df[_new].reset_index().to_csv(self.merged_frame, index=False)
        return fname

    def remove_quotes(self, file: os.PathLike) -> None:
        """Remove quotes from each line within the input file.

        Args:
            file: Path to file.
        """
        no_quotes = file.parent / "no_quotes.txt"
        with open(file) as fin, open(no_quotes, "w") as fout:
            for line in fin:
                line = line.replace('"', "")
                fout.write(line)
        shutil.move(no_quotes, file)

    def delta_score(self, grp: pd.DataFrame) -> pd.DataFrame:
        """Calculate the delta score.

        Args:
            grp: Input dataframe.

        Returns:
            Input dataframe + delta score columns.
        """
        grp = grp.sort_values("rank")
        grp["deltcn"] = (grp["score"] - grp.shift(-1)["score"]).fillna(0) / grp["score"]
        grp["deltlcn"] = (grp["score"] - min(grp["score"])) / grp["score"]
        grp["deltcn"] = grp["deltcn"].replace([np.inf, -np.inf], 0.0)
        grp["deltlcn"] = grp["deltlcn"].replace([np.inf, -np.inf], 0.0)
        return grp
