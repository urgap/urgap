"""Urgap dia_nn_library_prediction_1_8_1 wrapper."""

#!/usr/bin/env python

import os

import urgap

from urgap.wrappers.proteomics.database_search.dia_nn.dia_nn_1_8_1 import (
    dia_nn_1_8_1 as dia_nn_base,
)


class dia_nn_library_prediction_1_8_1(dia_nn_base):
    """Urgap wrapper for dia_nn_library_prediction_1_8_1.

    Uses DIA-NN from https://github.com/vdemichev/DiaNN

    """

    META_INFO = {
        "name": "dia_nn_library_prediction_1_8_1",
        "version": "1.8.1",
        "release_date": "20.02.2020",
        "wrapper_version": {"major": 1, "minor": 8, "patch": 1},
        "api_port": 42705,
        "engine_type": ("proteomics",),
        "platform_independent": False,
        "input_uftypes": {
            urgap.uftypes.proteomics.FASTA: {"min": 1, "max": -1},
        },
        "output_uftypes": {
            # will be checked after execution if all have been added using unode.add_auxiliary_output_file()
            urgap.uftypes.proteomics.diannlibrary.DIANN_PREDICTED_LIBRARY: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "diann_library_prediction_style_1",
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
                    #  ^--- this resources is used in the self.prep_urgap_package_structure method to convert the external resource to
                    #       an urgap resource
                    "external_md5": "a422bd1cf9336415c0ff492c0861e635",
                },
            },
        },
        "citation": "DIA-NN: neural networks and interference correction enable deep proteome coverage in high throughput Nature Methods, 2020",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialise the wrapper."""
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_command_arguments(
        translations: str,
        fasta_files: list,
        out_lib_filename: str,
    ) -> list:
        """Generate command line arguments for DIA-NN.

        Args:
            translations (str): Command line translation arguments.
            fasta_files (list): List of FASTA file paths.
            out_lib_filename (str): Output library filename.

        Returns:
            List of command line argument strings.
        """
        args = translations
        if not any(arg.startswith("--gen-spec-lib") for arg in args):
            msg = "--gen-spec-lib is a required argument"
            raise ValueError(msg)

        args += [f"--fasta {file}" for file in fasta_files]
        args += [f"--out-lib {out_lib_filename}"]
        return sorted(args)

    # def execute(self, urun_dict):
    #     """Execute routine for dia_nn_library_prediction_1_8_1 wrapper

    #     Optional. If not defined. urgap.unode.execute will be executed,
    #     which runs in principle a subprocess.run on urun_dict.command_list
    #     """
    #     execute_function_return_value = None
    #     return execute_function_return_value, urun_dict

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for dia_nn_library_prediction_1_8_1 wrapper.

        Optional if execute is defined in wrapper.
        Otherwise, use it to build the urun_dict.command_line!
        """
        self.add_modifications(utrace)
        translations = self.fix_translations(utrace)
        fasta_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.FASTA,
        )
        urgap_speclib_filename = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.diannlibrary.DIANN_PREDICTED_LIBRARY,
        )[0]
        args = self.get_command_arguments(
            translations,
            fasta_files,
            urgap_speclib_filename,
        )
        utrace.urun_dict.command_list = [str(self.exe_path), *args]
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for dia_nn_library_prediction_1_8_1 wrapper.

        Optional
        """
        urgap_speclib_filename = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.diannlibrary.DIANN_PREDICTED_LIBRARY,
        )[0]
        speclib_filename = urgap_speclib_filename.with_suffix(".predicted.speclib")

        os.rename(speclib_filename, urgap_speclib_filename)

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
            ufile (urgap.UFile): UFile object containing node execution data.

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
