"""Urgap dia_nn_report_generation_1_8_1 wrapper."""

#!/usr/bin/env python

import logging
import shutil

from pathlib import Path

import networkx as nx
import pandas as pd

import urgap

from urgap.wrappers.proteomics.database_search.dia_nn.dia_nn_1_8_1 import (
    dia_nn_1_8_1 as dia_nn_base,
)


class dia_nn_report_generation_1_8_1(dia_nn_base):
    """Urgap wrapper for dia_nn_report_generation_1_8_1.

    Uses DIA-NN from https://github.com/vdemichev/DiaNN

    """

    META_INFO = {
        "name": "dia_nn_report_generation_1_8_1",
        "version": "1.8.1",
        "release_date": "20.02.2020",
        "wrapper_version": {"major": 1, "minor": 8, "patch": 1},
        "api_port": 42706,
        "engine_type": ("proteomics",),
        "platform_independent": False,
        "input_uftypes": {
            urgap.uftypes.proteomics.dbsearch.DIANN_QUANT: {"min": 1, "max": -1},
            urgap.uftypes.proteomics.FASTA: {"min": 1, "max": -1},
            urgap.uftypes.proteomics.diannlibrary.ANY: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            # will be checked after execution if all have been added using unode.add_auxiliary_output_file()
            urgap.uftypes.proteomics.dbsearch.DIANN_REPORT: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "diann_report_generation_style_1",
        "engine": {
            "linux": {
                "arm64": {
                    "exe": "diann-1.8.1",
                    "uri": None,
                    "md5_checksum": "",
                    "additional_exe": {},
                    "external_url": "https://github.com/vdemichev/DiaNN/releases/download/1.8.1/diann_1.8.1.deb",
                    #  ^--- this resources is used in the self.prep_urgap_package_structure method to convert the external resource to
                    #       an urgap resource
                    "external_md5": "2aeb0832e385ab7e5e8cdc917698eb1f",
                },
                "x86_64": {
                    "exe": "diann-1.8.1",
                    "uri": None,
                    "md5_checksum": "",
                    "additional_exe": {},
                    "external_url": "https://github.com/vdemichev/DiaNN/releases/download/1.8.1/diann_1.8.1.deb",
                    #  ^--- this resources is used in the self.prep_urgap_package_structure method to convert the external resource to
                    #       an urgap resource
                    "external_md5": "2aeb0832e385ab7e5e8cdc917698eb1f",
                },
            },
            "win32": {
                "x86_64": {
                    "exe": "diann.exe",
                    "uri": None,
                    "md5_checksum": "",
                    "additional_exe": {},
                    "external_url": "https://github.com/vdemichev/DiaNN/releases/download/1.8.1/DIA-NN.1_8_1.Setup.exe",
                    "external_md5": "a422bd1cf9336415c0ff492c0861e635",
                    #  ^--- this resources is used in the self.prep_urgap_package_structure method to convert the external resource to
                    #       an urgap resource
                },
            },
        },
        "citation": "DIA-NN: neural networks and interference correction enable deep proteome coverage in high throughput Nature Methods, 2020",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialise the wrapper."""
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_command_arguments(
        translations: str,
        data_filenames: list,
        fasta_filenames: list,
        speclib_filenames: list,
        report_filename: str,
    ) -> list[str]:
        """Generate command line arguments for DIA-NN.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            List of command line argument strings.
        """
        EXCLUDED_ARGUMENTS = [
            "--gen-spec-lib",
            "--reannotate",
            # "--reanalyse",
            "--predictor",
            "--fasta-search",
        ]

        def is_excluded_argument(arg):
            is_excluded = False
            for excluded_argument in EXCLUDED_ARGUMENTS:
                if arg.strip().startswith(excluded_argument):
                    is_excluded = True
                    msg = f"Found excluded arg {arg}"
                    logging.debug(msg)
            return is_excluded

        args = translations

        REQUIRED_ARGS = []
        for required_arg in REQUIRED_ARGS:
            if not any(arg.startswith(required_arg) for arg in args):
                msg = f"add {required_arg} argument"
                logging.debug(msg)
                args += [required_arg]

        args = [arg for arg in args if not is_excluded_argument(arg)]

        if not any(arg.startswith("--use-quant") for arg in args):
            logging.debug("add --use-quant argument")
            args += ["--use-quant"]
        args += [f"--f {file}" for file in data_filenames]
        args += [f"--fasta {file}" for file in fasta_filenames]
        args += [f"--lib {file}" for file in speclib_filenames]
        args += [f"--out {report_filename}"]
        return sorted(args)

    # def execute(self, urun_dict):
    #     """Execute routine for dia_nn_report_generation_1_8_1 wrapper

    #     Optional. If not defined. urgap.unode.execute will be executed,
    #     which runs in principle a subprocess.run on urun_dict.command_list
    #     """
    #     execute_function_return_value = None
    #     return execute_function_return_value, urun_dict

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for dia_nn_report_generation_1_8_1 wrapper.

        Optional if execute is defined in wrapper.
        Otherwise, use it to build the urun_dict.command_line!
        """
        # Define all the filenames
        tmp_folder = Path("/tmp/diann")
        tmp_folder.mkdir(parents=True, exist_ok=True)
        urgap_quant_filenames = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.dbsearch.DIANN_QUANT,
        )
        for urgap_quant_filename in urgap_quant_filenames:
            shutil.move(
                urgap_quant_filename,
                tmp_folder / urgap_quant_filename.with_suffix(".d.quant").name,
            )
        fasta_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.FASTA,
        )
        urgap_quant_filenames = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.dbsearch.DIANN_QUANT,
        )
        urgap_report_filename = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.dbsearch.DIANN_REPORT,
        )[0]
        speclib_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.diannlibrary.ANY,
        )
        # Collect all command line arguments

        self.add_modifications(utrace)
        translations = self.fix_translations(utrace)
        args = self.get_command_arguments(
            translations=translations,
            data_filenames=[
                (tmp_folder / file.stem).as_posix() + ".d"
                for file in urgap_quant_filenames
            ],
            fasta_filenames=[file.as_posix() for file in fasta_files],
            speclib_filenames=[file.as_posix() for file in speclib_files],
            report_filename=urgap_report_filename.as_posix(),
        )
        utrace.urun_dict.command_list = [str(self.exe_path), *args]
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for dia_nn_report_generation_1_8_1 wrapper.

        Optional
        """
        # Map quant files to the original input file
        urgap_quant_objects = utrace.input_files.filter(
            {urgap.uftypes.proteomics.dbsearch.DIANN_QUANT: {}},
        )
        original_file_mapping = {}
        for urgap_quant_object in urgap_quant_objects:
            # Get possible parent files
            # - uftype is not annotated on the graph so use extension
            data_lineage_root = [
                root_file
                for root_file in urgap_quant_object.lineage_root_files
                if root_file.endswith(".tgz")
            ]
            # Get the full data graph
            ur = urgap.UReport(object_name=urgap_quant_object.object_name)
            # Kick out nodes which join data together and build subgraph
            selected_nodes = [
                n for n in ur.graph.nodes() if not n.startswith("dia_nn_library")
            ]
            G2 = ur.graph.subgraph(selected_nodes)
            # There should now be a single parent file with a direct path to the
            # incoming quant file
            parents = [
                root_file.split("/")[-1]
                for root_file in data_lineage_root
                if nx.has_path(G2, root_file, urgap_quant_object.object_name)
            ]
            original_file_mapping[
                urgap_quant_object.object_name.split("/")[-1][0:-6]
            ] = parents[0]
        urgap_report_filepath = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.dbsearch.DIANN_REPORT,
        )[0]
        df = pd.read_csv(urgap_report_filepath, sep="\t")
        df["Run"] = df["Run"].astype("category")
        df["Run"] = df["Run"].cat.rename_categories(original_file_mapping)
        df.to_csv(urgap_report_filepath, sep="\t", index=False)
        return utrace

    # def prep_urgap_package_structure(self, external_ufile_list: urgap.UFileList) -> urgap.UFileList:
    #     """Prepares resource specific package strucutre

    #     The wrapper can define a process which transforms the content
    #     of the external resource to the urgap resource format.

    #     This function is called from unode._prepare_urgap_packages, if
    #     available.

    #     Args:
    #         external_file_list (urgap.UFileList): unpacked external resource as ufiles

    #     Returns:
    #         urgap.UFileList: List of ufiles that should be ziped and shiped to the
    #             urgap_resources defined in the urgap.json
    #     """
    #     # # For example to add an additional file to the resource package:
    #     # new_wrapper_file = urgap.UFile(
    #     #     uri=external_ufile_list[0].as_uri(fragment="wrapper_file.txt", query="")
    #     # )
    #     # with open(new_wrapper_file.path, "w") as oo:
    #     #     print("<Example on how to modify Urgap Resource Package>", file=oo)

    #     # new_wrapper_file.upload()

    #     # external_ufile_list.append(new_wrapper_file)
    #     # return external_ufile_list

    @classmethod
    def generate_wrapper_vis(cls, ufile: urgap.UFile) -> list:
        """Generate basic nodes specific data visualization.

        This is used to produce a view into the data from the dashboard.

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
        return []
