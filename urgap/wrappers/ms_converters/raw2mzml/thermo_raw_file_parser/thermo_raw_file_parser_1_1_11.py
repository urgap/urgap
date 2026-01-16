"""Urgap umap_1_0_0 wrapper."""

import sys

import urgap


class thermo_raw_file_parser_1_1_11(urgap.unode.UNodeBase):
    """Urgap wrapper for the thermo_raw_file_parser_1_1_11 executable.

    ThermoRawFileParser can be used to convert Thermo.raw files to open XML-based
    format, mzml,  for encoding mass spectrometer data. See publication provided under
    META_INFO["citation"] for further info.

    The exe can be downloaded from:
        https://github.com/compomics/ThermoRawFileParser/releases/tag/v1.1.11

    Requires mono to be executed on linux systems!
    """

    META_INFO = {
        "name": "thermo_raw_file_parser_1_1_11",
        "version": "1.1.11",
        "release_date": "2019-09-25",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "api_port": 42403,
        "engine_type": ("converter",),
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "ThermoRawFileParser.exe",
                    "urn": "platform_independent/arc_independent/thermo_raw_file_parser_1_1_11.zip",
                    "urn_md5": "b498a722bedd1469efb025ef04da912e",
                    "external_md5": "4f51bdb2af14586efd5c1ba9d9b6d819",
                    "external_url": "https://github.com/compomics/ThermoRawFileParser/releases/download/v1.1.11/ThermoRawFileParser.zip",
                    "additional_exe": {},
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "other_dependencies": ("mono",),
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.THERMO_RAW: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML: {
                "min": 1,
                "max": 1,
            },
        },
        "create_own_folder": False,
        "utranslation_style": "thermo_raw_file_parser_style_1",
        "citation": """
        Hulstaert, N., Shofstahl, J., Sachsenberg, T., Walzer, M., Barsnes, H., Martens, L., & Perez-Riverol, Y. (2019). ThermoRawFileParser: Modular, Scalable, and Cross-Platform RAW File Conversion.
        In Journal of Proteome Research (Vol. 19, Issue 1, pp. 537-542). American Chemical Society (ACS). https://doi.org/10.1021/acs.jproteome.9b00328
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize thermo_raw_file_parser_1_1_11 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for thermo_raw_file_parser_1_1_11 wrapper.

        During preflight,
            - params are extracted from urun_dict
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        if sys.platform in ["win32"]:
            utrace.urun_dict.command_list = []
        else:
            utrace.urun_dict.command_list = ["mono"]

        input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.THERMO_RAW,
        )[0]
        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML,
        )[0]
        utrace.urun_dict.command_list.extend(
            [
                str(self.exe_path),
                f"-i={input_file!s}",
                f"-b={output_file!s}",
            ],
        )
        for urgap_name, param_dict in utrace.urun_dict.translations[
            "all_params"
        ].items():
            if urgap_name in ["thermo_raw_file_parser_options"]:
                for key, value in param_dict["translated_value"].items():
                    if value is not None:
                        utrace.urun_dict.command_list.append(f"{key}={value}")
                continue
            utrace.urun_dict.command_list.append(str(param_dict["translated_key"]))
            utrace.urun_dict.command_list.append(str(param_dict["translated_value"]))
        return utrace
