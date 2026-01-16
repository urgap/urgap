"""Urgap msgfplus_2021_03_22 wrapper."""

import contextlib
import os
import sys

from pathlib import Path

with contextlib.suppress(BaseException):
    from unimod_mapper import UnimodMapper

import urgap


class msgfplus_2021_03_22(urgap.unode.UNodeBase):
    """Urgap wrapper for the msgfplus_2021_03_22 search engine.

    MS-GF+ (aka MSGF+ or MSGFPlus) performs peptide identification by scoring MS/MS
    spectra against peptides derived from a protein sequence database. MS-GF+ is
    optimized for a variety of spectral types, i.e., combinations of fragmentation
    method, instrument, enzyme, and experimental protocols. See publication provided
    under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "msgfplus_2021_03_22",
        "version": "2021_03_22",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "14.04.2021",
        "api_port": 42711,
        "engine_type": ("db_search", "proteomics"),
        "platform_independent": True,  # !
        "requires": {
            "other_uftypes": {
                "other_dependencies": ("java",),
                "python_packages": [
                    "unimod_mapper",
                ],
            },
        },
        "resource_available": None,
        "utranslation_style": "msgfplus_style_1",
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "MSGFPlus.jar",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/msgfplus_2021_03_22.zip",
                    "urn_md5": "eaa47c12b40be7d731089e697be2f7b8",
                    "external_md5": None,
                    "external_url": None,
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.converter.PYMZML_MGF: {"min": 1, "max": 1},
            urgap.uftypes.proteomics.FASTA: {"min": 1, "max": 1},
            urgap.uftypes.proteomics.MODS_XML: {"min": 0, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.dbsearch.MSGFPLUS_MZID: {"min": 1, "max": 1},
        },
        "citation": """
        Kim, S., Mischerikow, N., Bandeira, N., Navarro, J. D., Wich, L., Mohammed, S., Heck, A. J. R., & Pevzner, P. A. (2010). The Generating Function of CID, ETD, and CID/ETD Pairs of Tandem Mass Spectra: Applications to Database Search.
        In Molecular Cellular Proteomics (Vol. 9, Issue 12, pp. 2840-2852). Elsevier BV. https://doi.org/10.1074/mcp.m110.003731
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize msgfplus_2021_03_22 class."""
        super().__init__(*args, **kwargs)

    def write_mod_file(
        self,
        utrace: urgap.UTrace,
    ) -> None:
        """Write mod file to be injested into the msgfplus search.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
        """
        self.mod_file = str(utrace.output_files[0].path) + "_Mods.txt"
        with open(self.mod_file, "w", encoding="UTF-8") as mods_file:
            modifications = []
            print(
                "NumMods={}".format(
                    utrace.urun_dict.translations["all_params"]["max_num_mods"][
                        "translated_value"
                    ],
                ),
                file=mods_file,
            )
            print("C3H5NO,U,custom,U,Selenocysteine", file=mods_file)

            # if udict["translated_cparameters"]["label"]["translated_value"] == "15N":
            #     for aminoacid, N15_Diff in urgap.ukb.DICT_15N_DIFF.items():
            #         existing = False
            #         for mod in udict["mapped_mods"]["fix"]:
            #             if aminoacid == mod["aa"]:
            #                 mod["mass"] += N15_Diff
            #                 mod["name"] += "_15N_{0}".format(aminoacid)
            #                 existing = True
            #         if existing == True:
            #             continue
            #         else:
            #             modifications.append(
            #                 "{0},{1},fix,any,15N_{1}".format(N15_Diff, aminoacid)
            #             )

            for mod_type in ["fix", "opt"]:
                for mod in self.mapped_mods[mod_type]:
                    modifications.append(
                        "{},{},{},{},{}".format(
                            mod["mass"],
                            mod["aa"],
                            mod_type,
                            mod["position"],
                            mod["name"],
                        ),
                    )

            for mod in modifications:
                print(mod, file=mods_file)

        self.tmp_files.append(self.mod_file)

    def reformat_mgf_input(
        self,
        utrace: urgap.UTrace,
    ) -> None:
        """Reformat the mgf input file, to be injested into the msgfplus search.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
        """
        mgf_file = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.converter.PYMZML_MGF,
        )[0]
        mgf_org_input_file = open(mgf_file, encoding="UTF-8")
        lines = mgf_org_input_file.readlines()
        mgf_org_input_file.close()

        frag_method = utrace.urun_dict.translations["all_params"]["frag_method"][
            "original_value"
        ].upper()
        self.mgf_new_input_file = str(mgf_file.parent / mgf_file.stem) + "_tmp.mgf"
        mgf_new_input_file = open(self.mgf_new_input_file, "w", encoding="UTF-8")
        for line in lines:
            if line.startswith("CHARGE"):
                print(line, file=mgf_new_input_file)
                print(
                    f"ACTIVATIONMETHOD={frag_method}",
                    file=mgf_new_input_file,
                )
            else:
                print(line, file=mgf_new_input_file)
        mgf_new_input_file.close()
        self.tmp_files.append(self.mgf_new_input_file)

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
        tcparams = utrace.urun_dict.translations["all_params"]

        utrace.urun_dict.command_list = [
            "java",
            "-jar",
            str(self.exe_path),
        ]
        clist = utrace.urun_dict.command_list

        for translated_key, translated_dict in tcparams.items():
            translated_dict_key = translated_dict["translated_key"]
            translated_dict_value = translated_dict["translated_value"]
            if translated_dict_key == "-Xmx":
                clist.insert(
                    1,
                    f"{translated_dict_key}{translated_dict_value}",
                )
            elif translated_key in [
                "label",
                "output_q_values",
                "header_translations",
                "mgf_input_file",
                "database",
                "modifications",
                "output_file_incl_path",
                "precursor_mass_tolerance_minus",
                "precursor_mass_tolerance_plus",
                "precursor_mass_tolerance_unit",
                "unimod_xml_file_list",
                "add_unimod_default_file",
            ] or (
                self.META_INFO["version"] in ["v2019_07_03"]
                and translated_key
                in [
                    "charge_carrier_mass",
                ]
            ):
                continue

            elif translated_key == "cpus":
                if translated_dict_value == "max - 1":
                    import multiprocessing

                    value = multiprocessing.cpu_count() - 1
                    clist.extend((translated_dict_key, value))
                else:
                    clist.extend((translated_dict_key, translated_dict_value))

            elif len(translated_dict) == 4 or "was_translated" in translated_dict:
                clist.extend((translated_dict_key, translated_dict_value))
            else:
                sys.exit(1)

        mgf_file = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.converter.PYMZML_MGF,
        )[0]
        fasta_file = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.FASTA,
        )[0]
        output_file = utrace.output_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.dbsearch.MSGFPLUS_MZID,
        )[0]

        clist.extend(
            [
                "-s",
                str(mgf_file),
                "-d",
                str(fasta_file),
                "-o",
                str(output_file),
                "-mod",
                self.mod_file,
            ],
        )
        clist.extend(
            (
                "-t",
                "{0}{1}, {2}{1}".format(
                    tcparams["precursor_mass_tolerance_minus"]["translated_value"],
                    tcparams["precursor_mass_tolerance_unit"]["translated_value"],
                    tcparams["precursor_mass_tolerance_plus"]["translated_value"],
                ),
            ),
        )
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for msgfplus_2021_03_22 wrapper.

        During preflight,
            - parameters are formatted
            - mods are mapped
            - helper files are written
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        unimod_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.MODS_XML,
        )
        self.mod_mapper = UnimodMapper(
            xml_file_list=unimod_files,
            add_default_files=utrace.urun_dict.translations["all_params"][
                "add_unimod_default_file"
            ]["translated_value"],
        )
        self.mapped_mods = self.mod_mapper.map_mods(
            utrace.urun_dict.translations["all_params"]["modifications"][
                "original_value"
            ],
        )
        self.write_mod_file(utrace=utrace)
        self.reformat_mgf_input(utrace=utrace)
        utrace = self.create_command_list(utrace=utrace)

        enzyme_txt_path = utrace.output_files[0].path.parent / "params" / "enzymes.txt"
        if enzyme_txt_path.exists() is False:
            os.symlink(
                Path(self.exe_path).parent / "Docs" / "Examples",
                utrace.output_files[0].path.parent / "params",
            )

        self.tmp_files.append(utrace.output_files[0].path.parent / "params")
        return utrace
