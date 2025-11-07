"""Urgap novor_1_05 wrapper."""

import logging
import os

import urgap


class novor_1_05(urgap.unode.UNodeBase):
    """Urgap wrapper for the novor_1_05 software tool.

    Novor is a sequencing software used in proteomics to sequence new peptides from
    tandem mass spectrometry data. See publication provided under META_INFO["citation"]
    for further info.
    """

    META_INFO = {
        "name": "novor_1_05",
        "version": "1.05",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "11.10.2015",
        "api_port": 42720,
        "engine_type": ("de_novo", "proteomics"),
        "platform_independent": False,  # !
        "requires": {
            "other_uftypes": {
                "other_dependencies": ("java",),
            },
        },
        "utranslation_style": "novor_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "novor.sh",
                    # "zip_md5": "",
                },
                "x86_64": {
                    "exe": "novor.sh",
                    # "zip_md5": "",
                },
            },
            "linux": {
                "arm64": {
                    "exe": "novor.sh",
                    # "zip_md5": "",
                },
                "x86_64": {
                    "exe": "novor.sh",
                    # "zip_md5": "",
                },
            },
            "win32": {
                "x86_64": {
                    "exe": "novor.bat",
                    # "zip_md5": "",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.converter.PYMZML_MGF: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.denovosearch.NOVOR_CSV: {"min": 1, "max": 1},
        },
        "citation": """
        Ma, B. (2015). Novor: Real-Time Peptide de Novo Sequencing Software.
        In Journal of the American Society for Mass Spectrometry (Vol. 26, Issue 11, pp. 1885-1894). American Chemical Society (ACS). https://doi.org/10.1007/s13361-015-1204-0
        """,
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize novor_1_05 class."""
        super().__init__(*args, **kwargs)

    def write_params_file(
        self,
        utrace: urgap.UTrace,
    ):
        """Write novor parameter file.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
        """
        self.params_file = str(utrace.output_files[0].path.parent / "Params.txt")

        params2write = set()
        tcparams = utrace.urun_dict.translations["all_params"]
        special_cases_dict = {}
        for _urgap_key, translated_dict in tcparams.items():
            translated_dict_key = translated_dict["translated_key"]
            translated_dict_value = translated_dict["translated_value"]

            if translated_dict_key in [
                "header_translations",
                "-f",
            ]:
                continue
            if (
                "precursorErrorTol" in translated_dict_key
                or "fragmentIonErrorTol" in translated_dict_key
            ):
                special_cases_dict[translated_dict_key] = translated_dict_value
            elif translated_dict_key == ("variableModifications", "fixedModifications"):
                available_mods = [
                    "Acetyl (K)",
                    "Acetyl (N-term)",
                    "Amidated (C-term)",
                    # 'Ammonia-loss (N-term C)',
                    "Biotin (K)",
                    "Biotin (N-term)",
                    "Carbamidomethyl (C)",
                    "Carbamyl (K)",
                    "Carbamyl (N-term)",
                    "Carboxymethyl (C)",
                    "Dioxidation (M)",
                    "Methyl (C-term)",
                    "Methyl (DE)",
                    "Oxidation (M)",
                    "Oxidation (HW)",
                    "Phospho (ST)",
                    "Phospho (Y)",
                    "Pyro-Glu (E)",
                    "Pyro-Glu (Q)",
                    "Sodium (C-term)",
                    "Sodium (DE)",
                    "Sulfo (STY)",
                    "Trimethyl (RK)",
                ]

                collected_mods = {"fix": [], "opt": []}
                for mod_type in collected_mods:
                    not_available_mods = {}
                    for mod in utrace.urun_dict.translations["mapped_mods"][mod_type]:
                        if mod["position"] == "N-term":
                            mod["aa"] = "N-term"
                        elif mod["position"] == "C-term":
                            mod["aa"] = "C-term"
                        elif mod["position"] != "any":
                            not_available_mods[mod["name"]].append(mod["aa"])
                            continue
                        if f"{mod['name']} ({mod['aa']})" not in available_mods:
                            if mod["name"] not in not_available_mods:
                                not_available_mods[mod["name"]] = []
                            not_available_mods[mod["name"]].append(mod["aa"])
                            continue
                        collected_mods[mod_type].append(
                            "{} ({})".format(mod["name"], mod["aa"]),
                        )

                    for mod in not_available_mods:
                        print(
                            """
                    [ WARNING ] Novor does not support your given modification
                    [ WARNING ] Continue without modification {} ({})""".format(
                                mod,
                                "".join(sorted(not_available_mods[mod])),
                            ),
                        )

                params2write.add(
                    f"variableModifications = {','.join(collected_mods['opt'])}",
                )
                params2write.add(
                    f"fixedModifications = {','.join(collected_mods['fix'])}",
                )

            else:
                params2write.add(f"{translated_dict_key} = {translated_dict_value}")

        for translated_dict_key, translated_dict_value in special_cases_dict.items():
            if "precursorErrorTol" in translated_dict_key:
                print(
                    """
                    [ WARNING ] precursor_mass_tolerance_plus and precursor_mass_tolerance_minus
                    [ WARNING ] need to be combined for Novor (use of symmetric tolerance window).
                    [ WARNING ] The arithmetic mean is used.
                    """,
                )
                precursor_mass_tolerance = (
                    float(special_cases_dict["precursorErrorTol_part1"])
                    + float(special_cases_dict["precursorErrorTol_part2"])
                ) / 2.0
                params2write.add(
                    f"precursorErrorTol = {precursor_mass_tolerance}{special_cases_dict['precursorErrorTol_part3']}",
                )
            elif "fragmentIonErrorTol" in translated_dict_key:
                if special_cases_dict["fragmentIonErrorTol_part2"] == "ppm":
                    frag_mass_tolerance_converted = urgap.util.convert_ppm_to_dalton(
                        special_cases_dict["fragmentIonErrorTol_part1"],
                        base_mz=utrace["unode_parameters"]["base_mz"],
                    )
                else:
                    frag_mass_tolerance_converted = special_cases_dict[
                        "fragmentIonErrorTol_part1"
                    ]
                params2write.add(
                    f"fragmentIonErrorTol = {frag_mass_tolerance_converted}Da",
                )

        with open(self.params_file, "w", encoding="UTF-8") as open_params_file:
            for param in sorted(params2write):
                print(param, file=open_params_file)

        self.tmp_files.append(self.params_file)

    def create_command_list(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Create the command list from input parameters.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        mgf_file = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.converter.PYMZML_MGF,
        )[0]
        utrace.urun_dict.command_list = [
            str(self.exe_path),
            "-p",
            str(self.params_file),
            str(mgf_file),
            "-f",
        ]
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ):
        """Preflight routine for novor_1_05 wrapper.

        During preflight,
            - parameters are formatted
            - param file is written
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
        """
        self.write_params_file(utrace=utrace)
        utrace = self.create_command_list(utrace=utrace)

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for novor_1_05 wrapper.

        During postflight the novor_1_05 output file is renamed into the pre-defined
        urgap output file.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        # rename output file, since output file name cannot be specified
        logging.info("Renaming output file ...")
        org_out_file = str(utrace.input_files[self.mgf_index].path) + ".csv"
        corrected_out_file = utrace.output_files[0].path
        os.rename(org_out_file, corrected_out_file)
        return utrace
