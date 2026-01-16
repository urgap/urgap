"""Urgap dia_nn_1_8_1 wrapper."""

# !/usr/bin/env python

import contextlib
import multiprocessing as mp
import os

with contextlib.suppress(BaseException):
    from unimod_mapper import UnimodMapper

import urgap


class dia_nn_1_8_1(urgap.unode.UNodeBase):
    """Urgap wrapper for dia_nn_1_8_1.

    Uses DIA-NN from https://github.com/vdemichev/DiaNN
    """

    META_INFO = {
        "name": "dia_nn_1_8_1",
        "version": "1.8.1",
        "release_date": "20.02.2020",
        "wrapper_version": {"major": 1, "minor": 8, "patch": 1},
        "api_port": 42702,
        "engine_type": ("proteomics",),
        "platform_independent": False,
        "input_uftypes": {
            urgap.uftypes.proteomics.BRUKER_D_TGZ: {"min": 1, "max": -1},
            urgap.uftypes.proteomics.FASTA: {"min": 1, "max": -1},
        },
        "output_uftypes": {
            # will be checked after execution if all have been added using unode.add_auxiliary_output_file()
            urgap.uftypes.proteomics.diannlibrary.DIANN_PREDICTED_LIBRARY: {
                "min": 1,  # TODO: SET THIS TO ZERO
                "max": 1,
            },
            urgap.uftypes.proteomics.diannlibrary.DIANN_EMPIRICIAL_LIBRARY: {
                "min": 1,  # TODO: SET THIS TO ZERO
                "max": 1,
            },
            urgap.uftypes.proteomics.dbsearch.DIANN_REPORT: {"min": 1, "max": 1},
        },
        "utranslation_style": "diann_style_1",
        "engine": {
            "linux": {
                "arm64": {
                    "exe": "diann-1.8.1",
                    "uri": None,
                    "urn": "linux/arm64/dia_nn_1_8_1.zip",
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
                    "urn": "linux/x86_64/dia_nn_1_8_1.zip",
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
                    "urn": "win32/x86_64/dia_nn_1_8_1.zip",
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
        fasta_filenames: list,
        data_filenames: list,
        report_filename: str,
        empirical_speclib_filename: os.PathLike,
    ) -> list[str]:
        """Generate command line arguments for DIA-NN.

        Args:
            translations (str): Command line translation arguments.
            fasta_filenames (list): List of FASTA file paths.
            data_filenames (list): List of data file paths.
            report_filename (str): Output report filename.
            empirical_speclib_filename (os.PathLike): Empirical spectral library filename.

        Returns:
            List of command line argument strings.
        """
        args = translations
        args += [f"--fasta {file.as_posix()}" for file in fasta_filenames]
        args += [f"--f {data_folder.as_posix()}" for data_folder in data_filenames]
        args += [f"--out {report_filename}"]
        args += [f"--out-lib {empirical_speclib_filename.with_suffix('')}"]
        return sorted(args)

    # def execute(self, urun_dict):
    #     """Execute routine for dia_nn_1_8_1 wrapper

    #     Optional. If not defined. urgap.unode.execute will be executed,
    #     which runs in principle a subprocess.run on urun_dict.command_list
    #     """
    #     execute_function_return_value = None
    #     return execute_function_return_value, urun_dict

    def format_modification(self, mod: dict) -> str:
        """Convert uparma to DIAN-NN modifications."""
        name = f"Unimod:{mod['id']}" if mod["unimod"] else mod["name"]
        if mod["aa"] == "*":
            if mod["position"] == "Prot-N-term":
                site = "*n"
            elif mod["position"] == "N-term":
                site = "n"
            else:
                msg = f"Unparsable position {mod['position']}"
                raise ValueError(msg)
        else:
            site = mod["aa"]
        mass = mod["mass"]
        return f"{name},{mass},{site}"

    def format_fixed_modifications(self) -> list:
        """Convert uparma to DIAN-NN fixed modifications."""
        arguments = []
        if hasattr(self, "mapped_mods") and "fix " in self.mapped_mods:
            mods = self.mapped_mods["fix"]
            arg_key = "--fixed-mod"
            for mod in mods:
                arg_value = self.format_modification(mod)
                arguments.append(f"{arg_key} {arg_value}".strip())
        return arguments

    def format_variable_modifications(self) -> list:
        """Convert uparma to DIAN-NN variable modifications."""
        arguments = []
        if hasattr(self, "mapped_mods") and "opt " in self.mapped_mods:
            mods = self.mapped_mods["opt"]
            arg_key = "--var-mod"
            for mod in mods:
                arg_value = self.format_modification(mod)
                arguments.append(f"{arg_key} {arg_value}".strip())
        return arguments

    def fix_translations(
        self,
        utrace: urgap.UTrace,
    ) -> list:
        """Translate uparma translations into actual executable arguments."""
        arguments = []
        translations = utrace.urun_dict.translations["all_params"]
        # Extract mods and convert to DIA-NN style
        modifications = (
            self.format_fixed_modifications() + self.format_variable_modifications()
        )
        if "modifications" in translations:
            del translations["modifications"]
        if "add_unimod_default_file" in translations:
            del translations["add_unimod_default_file"]
        # Merge mass tolerance plus/minus into absolute
        translations["precursor_mass_tolerance"] = {
            "original_style": "urgap_style_1",
            "original_key": "precursor_mass_tolerance_plus, precursor_mass_tolerance_minus",
            "original_value": (
                translations["precursor_mass_tolerance_plus"]["original_value"],
                translations["precursor_mass_tolerance_minus"]["original_value"],
            ),
            "translated_style": "diann_style_1",
            "translated_key": "--mass-acc-ms1",
            "translated_value": translations["precursor_mass_tolerance_minus"][
                "translated_value"
            ]
            + translations["precursor_mass_tolerance_plus"]["translated_value"],
        }
        del translations["precursor_mass_tolerance_plus"]
        del translations["precursor_mass_tolerance_minus"]

        # form command line argument strings
        for value in translations.values():
            translated_key = value["translated_key"]
            translated_value = value["translated_value"]
            if not translated_value:
                continue
            # Handle DROP_KEY tag
            if (translated_key is None) or ("<DROP_KEY>" in translated_key):
                translated_key = ""
            # Handle default CPU
            if value["translated_key"] is not None:
                if (value["original_key"] == "cpus") and (translated_value == -1):
                    translated_value = mp.cpu_count() - 1
            arguments.append(" ".join([translated_key, str(translated_value)]).strip())

        return arguments + modifications

    def add_modifications(
        self,
        utrace: urgap.UTrace,
    ) -> None:
        """Add modifications to urun_dict."""
        # Add unimod parsing
        self.mod_mapper = UnimodMapper(
            add_default_files=utrace.urun_dict.translations["all_params"][
                "add_unimod_default_file"
            ]["translated_value"],
        )
        self.mapped_mods = self.mod_mapper.map_mods(
            utrace.urun_dict.translations["all_params"]["modifications"][
                "original_value"
            ],
        )

    def uncompress_data(
        self,
        utrace: urgap.UTrace,
    ) -> list:
        """Decompress compressed tarballs."""
        data_files = utrace.input_files.filter(
            additional_filters={urgap.uftypes.proteomics.BRUKER_D_TGZ: ""},
        )
        data_folders = []
        for data_file in data_files:
            # Uncompress burker .d folder
            # Hope that first file is always in parent folder
            data_folders.append(data_file.uncompress()[0].path.parent)
        return data_folders

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for dia_nn_1_8_1 wrapper.

        Optional if execute is defined in wrapper.
        Otherwise, use it to build the urun_dict.command_line!
        """
        data_folders = self.uncompress_data(utrace)
        fasta_filenames = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.FASTA,
        )
        empirical_speclib_filename = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.diannlibrary.DIANN_EMPIRICIAL_LIBRARY,
        )[0]
        report_filename = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.dbsearch.DIANN_REPORT,
        )[0]
        self.add_modifications(utrace)
        translations = self.fix_translations(utrace)
        args = self.get_command_arguments(
            translations,
            fasta_filenames,
            data_folders,
            report_filename,
            empirical_speclib_filename,
        )
        utrace.urun_dict.command_list = [str(self.exe_path), *args]
        utrace.urun_dict["local_vars"] = {"data_folders": data_folders}
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for dia_nn_1_8_1 wrapper.

        Optional
        """
        predicted_speclib_filename = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.diannlibrary.DIANN_PREDICTED_LIBRARY,
        )[0]

        empirical_speclib_filename = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.diannlibrary.DIANN_EMPIRICIAL_LIBRARY,
        )[0]

        speclib_filename = empirical_speclib_filename.with_suffix("").with_suffix(
            ".predicted.speclib",
        )

        os.rename(speclib_filename, predicted_speclib_filename)

        return utrace

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
