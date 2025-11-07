"""Urgap omssa_2_1_9 wrapper."""

import logging
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

from pathlib import Path

import pandas as pd

try:
    from unimod_mapper import UnimodMapper
except:
    pass

import urgap


class omssa_2_1_9(urgap.unode.UNodeBase):
    """Urgap wrapper for the omssa_2_1_9 search engine.

    The Open Mass Spectrometry Search Algorithm (OMSSA) is an efficient search engine
    for identifying MS/MS peptide spectra by searching libraries of known protein
    sequences. OMSSA scores significant hits with a probability score developed using
    classical hypothesis testing, the same statistical method used in BLAST. See
    publication provided under META_INFO["citation"] for further info.

    Parameter options at http://www.ncbi.nlm.nih.gov/IEB/ToolBox/CPP_DOC/asn_spec/omssa.asn.html

    OMSSA 2.1.9 parameters at http://proteomicsresource.washington.edu/protocols06/omssa.php
    """

    META_INFO = {
        "name": "omssa_2_1_9",
        "version": "2.1.9",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "20.02.2020",
        "api_port": 42713,
        "engine_type": ("db_search", "proteomics"),
        "platform_independent": False,
        "utranslation_style": "omssa_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "omssacl",
                    "uri": None,
                    "urn": "darwin/arm64/omssa_2_1_9.zip",
                    "urn_md5": "403e1f1245f8e4a73ffedcd33c5d2c51",
                    "additional_exe": {"makeblastdb": "makeblastdb"},
                    "external_url": None,
                    "external_md5": None,
                },
                "x86_64": {
                    "exe": "omssacl",
                    "uri": None,
                    "urn": "darwin/x86_64/omssa_2_1_9.zip",
                    "urn_md5": "403e1f1245f8e4a73ffedcd33c5d2c51",
                    "additional_exe": {"makeblastdb": "makeblastdb"},
                    "external_url": None,
                    "external_md5": None,
                },
            },
            "linux": {
                "arm64": {
                    "exe": "omssacl",
                    "uri": None,
                    "urn": "linux/arm64/omssa_2_1_9.zip",
                    "urn_md5": "9a1b92cb35dae404ac7c98c27f122cb5",
                    "additional_exe": {"makeblastdb": "makeblastdb"},
                    "external_url": None,
                    "external_md5": None,
                },
                "x86_64": {
                    "exe": "omssacl",
                    "uri": None,
                    "urn": "linux/x86_64/omssa_2_1_9.zip",
                    "urn_md5": "9a1b92cb35dae404ac7c98c27f122cb5",
                    "additional_exe": {"makeblastdb": "makeblastdb"},
                    "external_url": None,
                    "external_md5": None,
                },
            },
            "win32": {
                "x86_64": {
                    "exe": "omssacl.exe",
                    "uri": None,
                    "urn": "win32/x86_64/omssa_2_1_9.zip",
                    "urn_md5": "55e020dacb4f72e9506db13459cd7c0c",
                    "additional_exe": {"makeblastdb": "makeblastdb"},
                    "external_url": None,
                    "external_md5": None,
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "unimod_mapper",
                ],
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.converter.PYMZML_MGF: {"min": 1, "max": 1},
            urgap.uftypes.proteomics.FASTA: {"min": 1, "max": 1},
            urgap.uftypes.proteomics.MODS_XML: {"min": 0, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.dbsearch.OMSSA_CSV: {"min": 1, "max": 1},
        },
        "mods_to_unimod_correction": {
            # this dict holds corrections of wrong OMSSA to unimod assignments
            "TMT 6-plex on K": {
                "unimod_id": "737",
                "ommsa_unimod_id": "738",  # this is TMT duplex in unimod
                "unimod_name": "TMT6plex",
            },
            "TMT 6-plex on n-term peptide": {
                "unimod_id": "737",
                "ommsa_unimod_id": "738",  # this is TMT duplex in unimod
                "unimod_name": "TMT6plex",
                "aa_targets": ["N-term"],  # override 'X' in OMSSA mods xml
            },
            "TMT duplex on K": {
                "unimod_id": "738",
                "ommsa_unimod_id": "738",  # this is TMT duplex in unimod
                "unimod_name": "TMT2plex",
            },
            "TMT duplex on n-term peptide": {
                "unimod_id": "738",
                "ommsa_unimod_id": "738",  # this is TMT duplex in unimod
                "unimod_name": "TMT2plex",
                "aa_targets": ["N-term"],  # override 'X' in OMSSA mods xml
            },
            "tmtpro of n-term": {
                "aa_targets": ["N-term"],
                "unimod_id": "2016",
                "unimod_name": "TMTpro",
            },
        },
        "citation": """
        Geer, L. Y., Markey, S. P., Kowalak, J. A., Wagner, L., Xu, M., Maynard, D. M., Yang, X., Shi, W., & Bryant, S. H. (2004). Open Mass Spectrometry Search Algorithm.
        In Journal of Proteome Research (Vol. 3, Issue 5, pp. 958-964). American Chemical Society (ACS). https://doi.org/10.1021/pr0499491
        """,
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize omssa_2_1_9 class."""
        super().__init__(*args, **kwargs)

    def _load_omssa_xml(
        self,
        utrace: urgap.UTrace,
    ) -> dict:
        """Parse through omssa mods to map omssa mods on unimods.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            Dict of omssa mods mapped to unimod.
        """
        omssa_mod_mapper = {}

        def _create_empty_tmp():
            tmp = {
                "aa_targets": [],
            }
            return tmp

        tmp = _create_empty_tmp()
        xml_paths = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.MODS_XML,
        )
        omssa_xml = Path(self.exe_path).parent.resolve() / "mods.xml"
        user_mods_xml = Path(self.exe_path).parent.resolve() / "usermods.xml"

        msg = f"Parsing omssa xml ({omssa_xml})"

        logging.info(msg)
        # for omssa_xml in [omssa_xml, user_mods_xml]:
        for omssa_xml in [user_mods_xml, *xml_paths]:
            for _event, element in ET.iterparse(str(omssa_xml)):
                # As I am not sure if xml.etree would take a Path object
                if element.tag.endswith("MSModSpec_residues_E"):
                    tmp["aa_targets"].append(element.text)

                elif element.tag.endswith("MSMod"):
                    tmp["omssa_id"] = element.text
                elif element.tag.endswith("MSModSpec_psi-ms"):
                    tmp["unimod_name"] = element.text
                elif element.tag.endswith("MSModSpec_unimod"):
                    tmp["unimod_id"] = element.text
                elif element.tag.endswith("MSModSpec_name"):
                    tmp["omssa_name"] = element.text
                    additional = []
                    if "protein" in tmp["omssa_name"]:
                        additional.append("Prot")
                    if "n-term" in tmp["omssa_name"]:
                        additional.append("N-term")
                    elif "c-term" in tmp["omssa_name"]:
                        additional.append("C-term")
                    if len(additional) > 0:
                        tmp["aa_targets"].append("-".join(additional))

                elif element.tag.endswith("MSModSpec"):
                    lookup_field = "unimod_id"
                    try:
                        l_value = tmp[lookup_field]
                    except:
                        msg = f"Skipping entry {tmp} (no unimod! map)"
                        logging.info(msg)
                        tmp["aa_targets"] = []
                        continue
                    if tmp["omssa_name"] in self.META_INFO["mods_to_unimod_correction"]:
                        l_value = self.META_INFO["mods_to_unimod_correction"][
                            tmp["omssa_name"]
                        ]["unimod_id"]
                        # for TMT mods OMSSA writes an 'X' as amino acid target, this breaks later code...
                        if (
                            "aa_targets"
                            in self.META_INFO["mods_to_unimod_correction"][
                                tmp["omssa_name"]
                            ]
                        ):
                            tmp["aa_targets"] = self.META_INFO[
                                "mods_to_unimod_correction"
                            ][tmp["omssa_name"]]["aa_targets"]
                    if l_value not in omssa_mod_mapper:
                        omssa_mod_mapper[l_value] = {}
                    omssa_mod_mapper[l_value][tmp["omssa_id"]] = {
                        "aa_targets": tmp["aa_targets"],
                        "omssa_name": tmp["omssa_name"],
                    }

                    tmp = _create_empty_tmp()
        return omssa_mod_mapper

    def make_blastdb(
        self,
        utrace: urgap.UTrace,
    ):
        """Generate helper files based on input fasta file, which are required by omssa.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
        """
        fasta_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.FASTA,
        )[0]

        blastdb_suffixes = [".phr", ".pin", ".psq"]
        blastdb_present = True
        for blastdb_suffix in blastdb_suffixes:
            blast_file = str(fasta_file) + blastdb_suffix
            if Path(blast_file).exists() is False:
                blastdb_present = False
                break

        if blastdb_present is False:
            command = [
                str(self.exe_path.parent.joinpath("makeblastdb")),
                "-in",
                str(fasta_file),
                "-dbtype",
                "prot",
                "-input_type",
                "fasta",
            ]
            logging.info("Executing makeblastdb...")
            logging.debug(" ".join(command))
            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
            )
            for line in proc.stdout:
                print(line.strip().decode("utf"))

    def write_usermods(
        self,
        omssa_usermods_xml: os.PathLike,
        mapped_mods: dict,
    ):
        """Write usermods into the omssa usermods xml file.

        Args:
            omssa_usermods_xml: Path where to write the usermods file.
            mapped_mods: Dict with mods in omssa vs unimod style.
        """
        attribs = {
            "xmlns:ns0": "http://www.ncbi.nlm.nih.gov",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.ncbi.nlm.nih.gov OMSSA.xsd",
        }
        mod_spec_set = ET.Element("MSModSpecSet", attrib=attribs)

        omssa_id = 208
        for mod_type in ["opt", "fix"]:
            for mod_dict in mapped_mods[mod_type]:
                element = self.generate_mod_element(mod_dict, omssa_id)
                omssa_id += 1
                mod_spec_set.append(element)
        with open(omssa_usermods_xml, "w") as f:
            new_tree = ET.ElementTree(mod_spec_set)
            # indent requires python >= 3.9
            new_tree.write(f, encoding="unicode")

    def generate_mod_element(
        self,
        mod_dict: dict,
        omssa_id: int,
    ) -> ET:
        """Generate a mod element to be written into mssa_usermods.xml.

        Args:
            mod_dict: Omssa mod to unimod conversion dict.
            omssa_id: Id to be assigned to the user omssa mod.

        Returns:
            Xml element describing the usermod.
        """
        mod_name = mod_dict["name"]
        aa = mod_dict["aa"]
        mono_mass = mod_dict["mass"]
        avg_mass = mod_dict["mass"]
        n15_mass = 0
        unimod_id = mod_dict["id"]

        # create root element
        ms_mod_spec_root = ET.Element("MSModSpec")

        # MSModSpec_mod
        ms_mod_spec_mod = ET.SubElement(ms_mod_spec_root, "MSModSpec_mod")
        ms_mod_spec_modname = ET.SubElement(
            ms_mod_spec_mod,
            "MSMod",
            attrib={"value": f"mod{omssa_id}"},
        )
        ms_mod_spec_modname.text = f"{omssa_id}"

        # MSModSpec_type
        ms_mod_spec_type = ET.SubElement(ms_mod_spec_root, "MSModSpec_type")
        # modaa for mods on aas, modnp for mods on peptide n-term, modn for mods on protein n-term
        translated_position = self.pos_translation[mod_dict["position"]]
        ms_mod_type = ET.SubElement(
            ms_mod_spec_type,
            "MSModType",
            {"value": translated_position},
        )
        if translated_position == "modaa":
            integer_pos = "0"
        elif translated_position == "modn":
            integer_pos = "1"
        elif translated_position == "modnp":
            integer_pos = "5"

        ms_mod_type.text = integer_pos  # what is this

        # MSModSpec_name
        ms_mod_spec_name = ET.SubElement(
            ms_mod_spec_root,
            "MSModSpec_name",
        )
        if mod_dict["position"] in ["N-term", "Prot-N-term"]:
            name = f"{mod_name.lower()} of {mod_dict['position'].lower()}"
        else:
            name = f"{mod_name.lower()} of {aa.upper()}"
        ms_mod_spec_name.text = name

        # MSModSpec_monomass
        ms_mod_spec_mono_mass = ET.SubElement(
            ms_mod_spec_root,
            "MSModSpec_monomass",
        )
        ms_mod_spec_mono_mass.text = f"{mono_mass}"

        # MSModSpec_averagemass
        ms_mod_spec_avg_mass = ET.SubElement(
            ms_mod_spec_root,
            "MSModSpec_averagemass",
        )
        ms_mod_spec_avg_mass.text = f"{avg_mass}"

        # MSModSpec_n15mass
        ms_mod_spec_n15_mass = ET.SubElement(ms_mod_spec_root, "MSModSpec_n15mass")
        ms_mod_spec_n15_mass.text = f"{n15_mass}"

        if mod_dict["position"] not in ["N-term", "Prot-N-term"]:
            # MSModSpec_residues
            ms_mod_spec_residues = ET.SubElement(ms_mod_spec_root, "MSModSpec_residues")
            ms_mod_spec_residues_e = ET.SubElement(
                ms_mod_spec_residues,
                "MSModSpec_residues_E",
            )
            if aa == "*":
                aa = "X"
            ms_mod_spec_residues_e.text = f"{aa}"

        # MSModSpec_unimod
        ms_mod_spec_unimod = ET.SubElement(
            ms_mod_spec_root,
            "MSModSpec_unimod",
        )
        ms_mod_spec_unimod.text = f"{unimod_id}"

        # MSModSpec_psi
        ms_mod_spec_psi_ms = ET.SubElement(ms_mod_spec_root, "MSModSpec_psi-ms")
        ms_mod_spec_psi_ms.text = f"{mod_name}"
        return ms_mod_spec_root

    def format_mods(
        self,
        utrace: urgap.UTrace,
    ) -> tuple:
        """Format mods into proper style, which is required by omssa.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            Dict in [mod type]: [omssa id] format, to be looked up in the lookups.
            Lookup dict with formatted mods in omssa format.
        """
        omssa_usermods_xml = Path(self.exe_path).parent.resolve() / "usermods.xml"
        self.write_usermods(omssa_usermods_xml, self.mapped_mods)
        self.omssa_mod_mapper_dict = self._load_omssa_xml(utrace)
        tmp_dict = {}
        utrace.urun_dict.translations["lookups"] = {}
        for mod_type in ["fix", "opt"]:
            modifications = ""
            tmp_dict[mod_type] = ""
            for mod_dict in self.mapped_mods[mod_type]:
                unimod_id_does_not_exist = False
                aa_can_not_be_mapped = True
                if mod_dict["id"] not in self.omssa_mod_mapper_dict:
                    unimod_id_does_not_exist = True
                else:
                    if mod_dict["aa"] == "*":
                        search_target = [
                            mod_dict["position"],
                        ]
                    else:
                        search_target = [
                            mod_dict["aa"],
                        ]
                    for omssa_id in self.omssa_mod_mapper_dict[mod_dict["id"]]:
                        if (
                            search_target
                            == self.omssa_mod_mapper_dict[mod_dict["id"]][omssa_id][
                                "aa_targets"
                            ]
                        ):
                            modifications += f"{omssa_id},"
                            aa_can_not_be_mapped = False
                            omssa_name = self.omssa_mod_mapper_dict[mod_dict["id"]][
                                omssa_id
                            ]["omssa_name"]
                            utrace.urun_dict.translations["lookups"][omssa_name] = {
                                "name": mod_dict["name"],
                                "aa_targets": self.omssa_mod_mapper_dict[
                                    mod_dict["id"]
                                ][omssa_id]["aa_targets"],
                                "omssa_id": omssa_id,
                                "id": mod_dict["id"],
                            }

                    if unimod_id_does_not_exist or aa_can_not_be_mapped:
                        logging.info(
                            """
                            The combination of modification name and aminoacid is not
                            supported by OMSSA. Continuing without modification: {}
                        """.format(mod_dict["id"]),
                        )
                        continue
            tmp_dict[mod_type] = modifications.strip(",")
        return tmp_dict, utrace.urun_dict.translations["lookups"]

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
        formatted_mods, self.correction_lookup = self.format_mods(utrace=utrace)
        utrace.urun_dict.command_list = [
            self.exe_path,  # path 2 omssa executable
            "-w",
        ]
        clist = utrace.urun_dict.command_list

        fasta_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.FASTA,
        )[0]
        mgf_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.converter.PYMZML_MGF,
        )[0]
        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.dbsearch.OMSSA_CSV,
        )[0]

        for _translated_key, translated_dict in tcparams.items():
            translated_dict_key = translated_dict["translated_key"]
            translated_dict_value = translated_dict["translated_value"]
            if translated_dict_key == ["-oc", "-ox"]:
                clist.extend(
                    (
                        translated_dict_value,
                        str(output_file),
                    ),
                )
                continue
            if translated_dict_key == "-d":
                clist.extend(
                    (
                        translated_dict_key,
                        str(fasta_file),
                    ),
                )
                continue
            if translated_dict_key == "-fm":
                clist.extend((translated_dict_key, str(mgf_file)))
                continue
            if translated_dict_key in ["-teppm", "-ni"]:
                if translated_dict_value != "":
                    clist.append(translated_dict_value)
                else:
                    continue
            elif translated_dict_key in [
                ("-mv", "mf"),
                [
                    "-mv",
                    "mf",
                ],
            ]:
                if formatted_mods["opt"] != "":
                    clist.extend(("-mv", formatted_mods["opt"]))
                if formatted_mods["fix"] != "":
                    clist.extend(("-mf", formatted_mods["fix"]))
                else:
                    continue
            elif translated_dict_key == ["-i", "-sct", "-sb1"]:
                ion_translation_dict = {
                    "a": "0",
                    "b": "1",
                    "c": "2",
                    "x": "3",
                    "y": "4",
                    "z": "5",
                }
                ions_2_add = [
                    ommsa_nr
                    for ion, ommsa_nr in ion_translation_dict.items()
                    if ion in translated_dict_value
                ]

                clist.extend(("-i", ",".join(sorted(ions_2_add))))
                if "b1" in translated_dict_value:
                    clist.extend(("-sb1", "0"))
                if "c_terminal" in translated_dict_value:
                    clist.extend(("-sct", "0"))
                continue
            elif translated_dict_key in [
                ["-tem", "-tom"],
                "-te_part1",
                "-te_part2",
                "semi_enzyme",
                "unimod_xml_file_list",
                "base_mz",
                "header_translations",
                "frag_mass_tolerance_unit",
                "output_file_incl_path",
                "-to",
                "-e",
                "add_unimod_default_file",
            ]:
                continue
            elif len(translated_dict) == 4 or "was_translated" in translated_dict:
                clist.extend((translated_dict_key, translated_dict_value))
            else:
                print(
                    "The translated key ",
                    translated_dict_key,
                    " maps on more than one ukey, but no special rules have been "
                    "defined",
                )
                print(translated_dict_value)
                sys.exit(1)

        # Format the cmd list
        if tcparams["enzyme_specificity"]["translated_value"] is True:
            if tcparams["enzyme"]["translated_value"] == "0":
                clist.extend(("-e", "16"))
            elif tcparams["enzyme"]["translated_value"] == "3":
                clist.extend(("-e", "23"))
            elif tcparams["enzyme"]["translated_value"] == "13":
                clist.extend(("-e", "24"))
        else:
            clist.extend(("-e", tcparams["enzyme"]["translated_value"]))

        if tcparams["frag_mass_tolerance_unit"]["translated_value"] == {"da": "Da"}:
            frag_mass_tolerance_converted = urgap.util.convert_ppm_to_dalton(
                tcparams["frag_mass_tolerance"]["translated_value"],
                base_mz=tcparams["base_mz"]["translated_value"],
            )
            clist.extend(("-to", frag_mass_tolerance_converted))
        else:
            clist.extend(("-to", tcparams["frag_mass_tolerance"]["translated_value"]))

        _omssa_precursor_error = (
            float(tcparams["precursor_mass_tolerance_minus"]["translated_value"])
            + float(tcparams["precursor_mass_tolerance_plus"]["translated_value"])
        ) / 2.0
        clist.extend(("-te", _omssa_precursor_error))
        print(
            """
            [ WARNING ] precursor_mass_tolerance_plus and precursor_mass_tolerance_minus
            [ WARNING ] need to be combined for pyQms (use of symmetric tolerance window).
            [ WARNING ] The arithmetic mean is used.
            """,
        )

        if mgf_file.exists() is False:
            raise OSError(
                """
                           OMSSA requires .mgf input (which should have been generated
                           automatically ...)""",
            )
        if fasta_file.exists() is False:
            raise OSError("""OMSSA requires a fasta database""")
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for omssa_2_1_9 wrapper.

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
        self.mod_mapper = UnimodMapper(xml_file_list=unimod_files)

        self.pos_translation = {
            "any": "modaa",
            "N-term": "modnp",
            "Prot-N-term": "modn",
        }

        self.mapped_mods = self.mod_mapper.map_mods(
            utrace.urun_dict.translations["all_params"]["modifications"][
                "original_value"
            ],
        )
        utrace = self.create_command_list(utrace=utrace)
        self.make_blastdb(utrace=utrace)
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for omssa_2_1_9 wrapper.

        During postflight the N-term modification is corrected as omssa does not
        report it in a unified way that is required for further processing.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        # TODO mv backup unimod to its original name
        logging.info("Correcting OMSSA Unimod mappings...")
        replace_n_term = {
            f"{omssa_name}:1": f"{mapping['name']}:0"
            for omssa_name, mapping in self.correction_lookup.items()
            if any("N-term" in targ for targ in mapping["aa_targets"])
        }
        replace_dict = {
            omssa_name: mapping["name"]
            for omssa_name, mapping in self.correction_lookup.items()
        }
        df = pd.read_csv(utrace.output_files[0].path)
        # That space is totally omssas fault
        df[" Mods"] = df[" Mods"].replace(replace_n_term, regex=True)
        df[" Mods"] = df[" Mods"].replace(replace_dict, regex=True)
        df.to_csv(utrace.output_files[0].path, index=False)
        return utrace
