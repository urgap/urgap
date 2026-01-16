"""Urgap dia_nn_file_quantification_1_8_1 wrapper."""

#!/usr/bin/env python

import os

import urgap

from urgap.wrappers.proteomics.database_search.dia_nn.dia_nn_1_8_1 import (
    dia_nn_1_8_1 as dia_nn_base,
)


class dia_nn_file_quantification_1_8_1(dia_nn_base):
    """Urgap wrapper for dia_nn_file_quantification_1_8_1.

    Uses DIA-NN from https://github.com/vdemichev/DiaNN
    """

    META_INFO = {
        "name": "dia_nn_file_quantification_1_8_1",
        "version": "1.8.1",
        "release_date": "20.02.2020",
        "wrapper_version": {"major": 1, "minor": 8, "patch": 1},
        "api_port": 42703,
        "engine_type": ("proteomics",),
        "platform_independent": False,
        "input_uftypes": {
            urgap.uftypes.proteomics.BRUKER_D_TGZ: {"min": 1, "max": 1},
            urgap.uftypes.proteomics.FASTA: {"min": 0, "max": -1},
            urgap.uftypes.proteomics.diannlibrary.ANY: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            # will be checked after execution if all have been added using unode.add_auxiliary_output_file()
            urgap.uftypes.proteomics.dbsearch.DIANN_QUANT: {"min": 1, "max": 1},
        },
        "utranslation_style": "diann_quantification_style_1",
        "engine": {
            "linux": {
                "arm64": {
                    "exe": "diann-1.8.1",
                    "uri": None,
                    "urn": "linux/arm64/dia_nn_file_quantification_1_8_1.zip",
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
                    "urn": "linux/x86_64/dia_nn_file_quantification_1_8_1.zip",
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
                    "urn": "win32/x86_64/dia_nn_file_quantification_1_8_1.zip",
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
        data_folders: list,
        speclib_files: list,
        fasta_files: list,
    ) -> list:
        """Generate command line arguments for DIA-NN.

        Args:
            translations (str): Command line translation arguments.
            data_folders (list): List of data folder paths.
            speclib_files (list): List of spectral library file paths.
            fasta_files (list): List of FASTA file paths.

        Returns:
            List of command line argument strings.
        """
        args = translations
        args += [f"--f {data_folder.as_posix()}" for data_folder in data_folders]
        args += [f"--lib {file.as_posix()}" for file in speclib_files]
        args += [f"--fasta {file.as_posix()}" for file in fasta_files]
        return sorted(args)

    # def execute(self, urun_dict):
    #     """Execute routine for dia_nn_file_quantification_1_8_1 wrapper

    #     Optional. If not defined. urgap.unode.execute will be executed,
    #     which runs in principle a subprocess.run on urun_dict.command_list
    #     """
    #     execute_function_return_value = None
    #     return execute_function_return_value, urun_dict

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for dia_nn_file_quantification_1_8_1 wrapper.

        Optional if execute is defined in wrapper.
        Otherwise, use it to build the urun_dict.command_line!
        """
        # self.param_file_path = self.write_config_file(utrace: urgap.UTrace,) -> urgap.UTrace
        data_files = utrace.input_files.filter(
            additional_filters={urgap.uftypes.proteomics.BRUKER_D_TGZ: ""},
        )
        data_folders = []
        for data_file in data_files:
            # Uncompress burker .d folder
            # Hope that first file is always in parent folder
            data_folders.append(data_file.uncompress()[0].path.parent)

        speclib_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.diannlibrary.ANY,
        )
        fasta_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.FASTA,
        )
        translations = self.fix_translations(utrace)
        args = self.get_command_arguments(
            translations,
            data_folders,
            speclib_files,
            fasta_files,
        )
        utrace.urun_dict.command_list = [str(self.exe_path), *args]
        utrace.urun_dict["local_vars"] = {"data_folders": data_folders}
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for dia_nn_file_quantification_1_8_1 wrapper.

        Optional
        """
        data_folders = utrace.urun_dict["local_vars"]["data_folders"]
        for ii in range(len(data_folders)):
            urgap_output_quant_filename = (
                utrace.output_files.get_path_objects_by_uftype(
                    urgap.uftypes.proteomics.dbsearch.DIANN_QUANT,
                )[ii]
            )
            pipeline_quant_filename = data_folders[ii].with_suffix(".d.quant")
            os.rename(pipeline_quant_filename, urgap_output_quant_filename)

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
    #

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
