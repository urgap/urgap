"""Urgap pyiohat_1_7_1 wrapper."""

import json
import logging

import pandas as pd

import urgap


class pyiohat_1_7_1(urgap.unode.UNodeBase):
    """Urgap wrapper for the pyiohat_1_7_1 resource.

    This wrapper calls the main resource to pyProtista csv files coming from different
    proteomics search engines. The purpose is to bring the search engine specific
    names into a unified format for further processing and merging of data.
    """

    META_INFO = {
        "name": "pyiohat_1_7_1",
        "version": "1.0.0",
        "release_date": "12.10.2022",
        "wrapper_version": {"major": 1, "minor": 1, "patch": 0},
        "api_port": 42721,
        "engine_type": ("converter", "proteomics"),
        "platform_independent": True,
        "engine": {
            "platform_independent": {"arc_independent": {"exe": "pyiohat_1_7_1.py"}},
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "unimod_mapper",
                    "pyiohat",
                ],
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.dbsearch.ANY: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.proteomics.quantification.FLASHLFQ_PSM_TSV: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.proteomics.MODS_XML: {"min": 0, "max": -1},
            urgap.uftypes.ms.SPECTRA_META_CSV: {"min": 1, "max": -1},
            urgap.uftypes.proteomics.FASTA: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.converter.PYIOHAT_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "pyiohat_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pyiohat_1_7_1 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pyiohat_1_7_1 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        search_input_file = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.dbsearch.ANY,
        )
        quant_input_file = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.quantification.FLASHLFQ_PSM_TSV,
        )

        if len(search_input_file) == 1 and len(quant_input_file) == 0:
            input_file = search_input_file[0]
        elif len(search_input_file) == 0 and len(quant_input_file) == 1:
            input_file = quant_input_file[0]
        else:
            logging.warning("Needs at least one quant input or one search input file")

        fasta_file = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.FASTA,
        )[0]
        meta_data_files = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.ms.SPECTRA_META_CSV,
        )

        # will probably be overridden for multiple runs
        # make temp file or add hash?
        concatenated_meta = pd.concat([pd.read_csv(file) for file in meta_data_files])
        tmp_md_file = str(utrace.output_files[0].path) + "_md.csv"
        concatenated_meta.to_csv(tmp_md_file, index=False)
        self.tmp_files.append(tmp_md_file)

        xml_file_list = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.MODS_XML,
        )
        output_file = utrace.output_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.converter.PYIOHAT_CSV,
        )[0]

        param_string = json.dumps(utrace.urun_dict.translations["all_params"])
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(input_file),
            "-f",
            str(fasta_file),
            "-md",
            str(tmp_md_file),
            "-o",
            str(output_file),
            "-p",
            param_string,
        ]

        for xml_file in xml_file_list:
            utrace.urun_dict.command_list.extend(["-x", str(xml_file)])

        return utrace
