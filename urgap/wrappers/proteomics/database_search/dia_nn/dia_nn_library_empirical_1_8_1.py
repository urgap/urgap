"""Urgap dia_nn_library_empirical_1_8_1 wrapper."""

# !/usr/bin/env python

import shutil

import urgap

from urgap.wrappers.proteomics.database_search.dia_nn.dia_nn_1_8_1 import (
    dia_nn_1_8_1 as dia_nn_base,
)


class dia_nn_library_empirical_1_8_1(dia_nn_base):
    """Urgap wrapper for dia_nn_library_empirical_1_8_1.

    Uses DIA-NN from https://github.com/vdemichev/DiaNN

    """

    ####
    META_INFO = {
        "name": "dia_nn_library_empirical_1_8_1",
        "version": "1.8.1",
        "release_date": "20.02.2020",
        "wrapper_version": {"major": 1, "minor": 8, "patch": 1},
        "api_port": 42704,
        "engine_type": ("proteomics",),
        "platform_independent": False,
        "input_uftypes": {
            urgap.uftypes.proteomics.dbsearch.DIANN_QUANT: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.proteomics.diannlibrary.ANY: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            # will be checked after execution if all have been added using unode.add_auxiliary_output_file()
            urgap.uftypes.proteomics.diannlibrary.DIANN_EMPIRICIAL_LIBRARY: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "diann_library_empirical_style_1",
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
        outlib_speclib_filename: str,
        data_filenames: list,
        speclib_filenames: list,
    ) -> list:
        """Generate command line arguments for DIA-NN.

        Args:
            translations (str): Command line translation arguments.
            outlib_speclib_filename (str): Output spectral library filename.
            data_filenames (list): List of data file paths.
            speclib_filenames (list): List of spectral library file paths.

        Returns:
            List of command line argument strings.
        """
        args = translations

        REQUIRED_ARGS = ["--use-quant", "--gen-spec-lib"]
        for required_arg in REQUIRED_ARGS:
            if not any(arg.startswith(required_arg) for arg in args):
                msg = f"missing argument {required_arg}"
                raise ValueError(msg)

        args += [f"--f {file}" for file in data_filenames]
        args += [f"--lib {file}" for file in speclib_filenames]
        args += [f"--out-lib {outlib_speclib_filename}"]
        return sorted(args)

    # def execute(self, urun_dict):
    #     """Execute routine for dia_nn_library_empirical_1_8_1 wrapper

    #     Optional. If not defined. urgap.unode.execute will be executed,
    #     which runs in principle a subprocess.run on urun_dict.command_list
    #     """
    #     execute_function_return_value = None
    #     return execute_function_return_value, urun_dict

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for dia_nn_library_empirical_1_8_1 wrapper.

        Optional if execute is defined in wrapper.
        Otherwise, use it to build the urun_dict.command_line!
        """
        # All quant files need to be in a temp folder
        from pathlib import Path

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

        speclib_filenames = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.diannlibrary.ANY,
        )
        urgap_quant_filenames = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.dbsearch.DIANN_QUANT,
        )
        output_speclib_filename = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.diannlibrary.DIANN_EMPIRICIAL_LIBRARY,
        )[0]

        data_filenames = [
            (tmp_folder / file.stem).as_posix() + ".d" for file in urgap_quant_filenames
        ]
        self.add_modifications(utrace)
        translations = self.fix_translations(utrace)
        args = self.get_command_arguments(
            translations,
            output_speclib_filename.with_suffix("").as_posix(),
            data_filenames,
            speclib_filenames,
        )
        utrace.urun_dict.command_list = [str(self.exe_path), *args]
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for dia_nn_library_empirical_1_8_1 wrapper.

        Overwrite base diann class
        """
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
