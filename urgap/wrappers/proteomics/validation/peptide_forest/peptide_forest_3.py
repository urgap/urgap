"""Urgap peptide_forest_3 wrapper."""

import json
import os

import pandas as pd

import urgap


class peptide_forest_3(urgap.unode.UNodeBase):
    """Urgap wrapper for the peptide_forest_3 module.

    Peptide Forest is a machine learning based tool for semisupervised integration of
    multiple peptide identification search engines. See publication
    provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "peptide_forest_3",
        "version": "3.0.0",
        "release_date": "22.12.2022",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "api_port": 42730,
        "engine_type": ("validation", "proteomics"),
        "platform_independent": True,
        "engine": {
            "platform_independent": {
                "arc_independent": {"exe": "peptide_forest_3_0_0.py"},
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "unimod_mapper",
                    "peptide_forest",
                ],
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.converter.PYIOHAT_CSV: {"min": 1, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.validator.PEPTIDEFOREST_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "peptide_forest_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize peptide_forest_3 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for percolator_3_5_0 wrapper.

        During preflight,
            - peptideforest config_json is written
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        config_json = self._write_config_json(utrace)
        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.validator.PEPTIDEFOREST_CSV,
        )[0]
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-c",
            str(config_json),
            "-o",
            str(output_file),
        ]
        return utrace

    def _write_config_json(
        self,
        utrace: urgap.UTrace,
    ) -> os.PathLike:
        """Write config_json required by peptideforest.

        The function formats user input parameters into peptideforest style and writes
        them out into a config_json file required for peptideforest execution.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            Path to config_json.
        """
        data = {"input_files": {}}

        # Store input files with corresponding validation score column and engine name
        score_fields = utrace.urun_dict.translations["all_params"][
            "validation_score_field"
        ]["translated_value"]
        for file in utrace.input_files:
            df = pd.read_csv(str(file.path), nrows=1)
            se = df.iloc[0]["search_engine"]
            data["input_files"].setdefault(str(file.path), {})["engine"] = se
            data["input_files"].setdefault(str(file.path), {})["score_col"] = (
                score_fields[se]
            )

        # Add remaining configuration parameters
        for urgap_name, pdict in utrace.urun_dict.translations["all_params"].items():
            if urgap_name in ["bigger_scores_better", "validation_score_field"]:
                continue
            data[pdict["translated_key"]] = pdict["translated_value"]

        config_path = utrace.output_files[0].path.parent / "config.json"
        with open(config_path, "w") as fh:
            json.dump(data, fh)
        return config_path
