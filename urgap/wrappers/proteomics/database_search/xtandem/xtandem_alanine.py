"""Urgap xtandem_alanine wrapper."""

import copy
import logging

try:
    from unimod_mapper import UnimodMapper
except:
    pass

import urgap


class xtandem_alanine(urgap.unode.UNodeBase):
    """Urgap wrapper for the xtandem_alanine search engine.

    X! Tandem is an open source software that can match tandem mass spectra with
    peptide sequences, in a process that has come to be known as protein identification.
    See publication provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "xtandem_alanine",
        "version": "alanine",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "20.02.2020",
        "api_port": 42714,
        "engine_type": ("db_search", "proteomics"),
        "platform_independent": False,
        "utranslation_style": "xtandem_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "tandem",
                    "urn": "darwin/arm64/xtandem_alanine.zip",
                    "urn_md5": "f4eb5f76cf805ba8d9424eb8c43a5cdf",
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "tandem",
                    "urn": "darwin/x86_64/xtandem_alanine.zip",
                    "urn_md5": "f4eb5f76cf805ba8d9424eb8c43a5cdf",
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "linux": {
                "arm64": {
                    "exe": "tandem.exe",
                    "urn": "linux/arm64/xtandem_alanine.zip",
                    "urn_md5": "22a4d6af7da2e6ac1ca54079b2031ca9",
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "tandem.exe",
                    "urn": "linux/x86_64/xtandem_alanine.zip",
                    "urn_md5": "22a4d6af7da2e6ac1ca54079b2031ca9",
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "win32": {
                "x86_64": {
                    "exe": "tandem.exe",
                    "urn": "win32/x86_64/xtandem_alanine.zip",
                    "urn_md5": "2ad9508810b2a6f1fa6df7c6ad5a4f56",
                    "external_md5": None,
                    "external_url": None,
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
            urgap.uftypes.proteomics.dbsearch.XTANDEM_XML: {"min": 1, "max": 1},
        },
        "citation": """
        Craig, R., & Beavis, R. C. (2004). TANDEM: matching proteins with tandem mass spectra.
        In Bioinformatics (Vol. 20, Issue 9, pp. 1466-1467). Oxford University Press (OUP). https://doi.org/10.1093/bioinformatics/bth092
        """,
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize xtandem_alanine class."""
        super().__init__(*args, **kwargs)

    def format_mods(
        self,
        utrace: urgap.UTrace,
    ) -> dict:
        """Format mods into proper style, which is required by mascot.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            Dict with formatted mods in xtandem format.
        """
        formatted_mods = {}
        potential_mods = []
        refine_potential_mods = []
        fixed_mods = []
        formatted_mods["Prot-N-term"] = {
            "translated_key": "protein, N-terminal residue modification mass",
            "translated_value": 0,
        }
        formatted_mods["Prot-C-term"] = {
            "translated_key": "protein, C-terminal residue modification mass",
            "translated_value": 0,
        }
        for mod in self.mapped_mods["fix"]:
            if self.META_INFO["version"] in ["vengeance", "alanine"]:
                if mod["position"] == "N-term":
                    mod["aa"] = "["
                elif mod["position"] == "C-term":
                    mod["aa"] = "]"
                fixed_mods.append("{}@{}".format(mod["mass"], mod["aa"]))
            else:
                fixed_mods.append("{}@{}".format(mod["mass"], mod["aa"]))
        formatted_mods["acetyl_N_term"] = {
            "translated_key": "protein, quick acetyl",
            "translated_value": "no",
        }
        formatted_mods["pyro_glu"] = {
            "translated_key": "protein, quick pyrolidone",
            "translated_value": "no",
        }
        pyro_glu = 0
        potentially_modified_aa = set()
        for mod in self.mapped_mods["opt"]:
            if (
                mod["aa"] == "*"
                and mod["name"] == "Acetyl"
                and mod["position"] == "Prot-N-term"
            ):
                formatted_mods["acetyl_N_term"]["translated_value"] = "yes"
                continue
            if (
                mod["aa"] == "*"
                and mod["name"] == "Gln->pyro-Glu"
                and mod["position"] == "N-term"
            ):
                pyro_glu += 1
                continue
            if (
                mod["aa"] == "*"
                and mod["name"] == "Glu->pyro-Glu"
                and mod["position"] == "N-term"
            ):
                pyro_glu += 1
                continue
            for term in ["Prot-N-term", "Prot-C-term"]:
                if mod["position"] == term:
                    if mod["aa"] == "*":
                        if formatted_mods[term]["translated_value"] != 0:
                            print(
                                """
            [ WARNING ] X!Tandem does not allow two mods on the same position {1}
            [ WARNING ] Continue without modification {0} """.format(mod, term, **mod),
                            )
                            continue
                        formatted_mods[term]["translated_value"] = mod["mass"]
                    else:
                        print(
                            """
            [ WARNING ] X!Tandem does not support specific aminoacids for terminal modifications
            [ WARNING ] Continue without modification {} """.format(mod, **mod),
                        )
                        continue
            if mod["aa"] in potentially_modified_aa:
                print(
                    """
            [ WARNING ] X!Tandem does not allow two potential mods on the same aminoacid!
            [ WARNING ] Continue without modification {} """.format(mod, **mod),
                )
                continue
            if self.META_INFO["version"] in ["vengeance", "alanine"]:
                forbidden_cterm_list = utrace.urun_dict.parameters.get(
                    "forbidden_cterm_mods",
                    [],
                )
                forbidden_cterm = ""
                max_num_per_mod_name_specific_dict = utrace.urun_dict.parameters.get(
                    "max_num_per_mod_name_specific",
                    {},
                )
                max_num_per_mod_name_specific = ""
                if mod["name"] in forbidden_cterm_list:
                    forbidden_cterm = "]"
                if mod["name"] in max_num_per_mod_name_specific_dict:
                    max_num_per_mod_name_specific = (
                        max_num_per_mod_name_specific_dict.get(mod["name"], "")
                    )

                if mod["position"] == "N-term":
                    mod["aa"] = "["
                elif mod["position"] == "C-term":
                    mod["aa"] = "]"

                potential_mods.append(
                    "{}@{}{}{}".format(
                        mod["mass"],
                        max_num_per_mod_name_specific,
                        forbidden_cterm,
                        mod["aa"],
                    ),
                )
                potentially_modified_aa.add(mod["aa"])
            else:
                potential_mods.append("{}@{}".format(mod["mass"], mod["aa"]))
                potentially_modified_aa.add(mod["aa"])

            if pyro_glu == 2:
                formatted_mods["pyro_glu"]["translated_value"] = "yes"
            if pyro_glu == 1:
                print(
                    """
        [ WARNING ] X!Tandem looks for Gln->pyro-Glu and Glu->pyro-Glu
        [ WARNING ] at the same time, please include both or none
        [ WARNING ] Continue without modification {} """.format(mod, **mod),
                )

        formatted_mods["fixed_modifications"] = {
            "translated_key": "residue, modification mass",
            "translated_value": ",".join(fixed_mods),
        }
        formatted_mods["potential_modifications"] = {
            "translated_key": "residue, potential modification mass",
            "translated_value": ",".join(potential_mods),
        }
        formatted_mods["refine_potential_modifications"] = {
            "translated_key": "refine, potential modification mass",
            "translated_value": ",".join(refine_potential_mods),
        }
        if "ptm_complexity" in utrace.urun_dict.parameters:
            max_mod_alternatives = utrace.urun_dict.parameters["ptm_complexity"]
        else:
            max_mod_alternatives = 6.0

        formatted_mods["max_mod_alternatives"] = {
            "translated_key": "protein, ptm complexity",
            "translated_value": max_mod_alternatives,
        }

        return formatted_mods

    def define_xml_templates(
        self,
        utrace: urgap.UTrace,
    ) -> dict:
        """Define the template for the xtandem param xml files.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            Dict with [xml_template]: [path_to_xml_template] info.
        """
        xml_required = [
            "default_input.xml",
            "taxonomy.xml",
            "15N-masses.xml",
            "input.xml",
        ]
        xml_dict = {}
        for file_name in xml_required:
            file_info_key = file_name.replace(".xml", "")
            xml_file_path = utrace.output_files[0].path.parent / file_name
            xml_dict[file_info_key] = {
                "translated_key": file_info_key,
                "translated_value": f"{xml_file_path}",
            }
        return xml_dict

    def write_xml_templates(
        self,
        utrace: urgap.UTrace,
    ):
        """Write templates - param files required by xtandem search engine.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
        """
        templates = self.format_templates(utrace=utrace)
        for file_name, content in templates.items():
            # if (
            #     file_name == "15N-masses.xml"
            #     and urun_dict["formatted_translated_cparameters"]["label"][
            #         "translated_value"
            #     ]
            #     == "14N"
            # ):
            #     continue
            xml_file_path = utrace.urun_dict.translations["formatted_params"][
                file_name
            ]["translated_value"]
            with open(xml_file_path, "w") as out:
                print(content, file=out)
                msg = f"Wrote input file {file_name}"
                logging.info(msg)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for xtandem_alanine wrapper.

        During preflight,
            - parameters are formatted
            - mods are mapped and formatted
            - param files are written
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

        utrace = self.format_params(utrace=utrace)
        utrace.urun_dict.translations["formatted_params"].update(
            self.format_mods(utrace=utrace),
        )
        utrace.urun_dict.translations["formatted_params"].update(
            self.define_xml_templates(utrace=utrace),
        )
        self.write_xml_templates(utrace=utrace)

        # Define the command list
        utrace.urun_dict.command_list = [
            f"{self.exe_path}",
            "{input[translated_value]}".format(
                **utrace.urun_dict.translations["formatted_params"],
            ),
        ]
        return utrace

    def format_params(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Format params into a format expected by the xtandem search engine.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.translations["formatted_params"] = copy.deepcopy(
            utrace.urun_dict.translations["all_params"],
        )
        ftcparams = utrace.urun_dict.translations["formatted_params"]

        mgf_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.converter.PYMZML_MGF,
        )[0]
        fasta_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.FASTA,
        )[0]
        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.dbsearch.XTANDEM_XML,
        )[0]

        ftcparams["mgf_input_file"]["translated_value"] = str(mgf_file)

        ftcparams["database"]["translated_value"] = str(fasta_file)

        ftcparams["output_file_incl_path"]["translated_value"] = str(output_file)

        if ftcparams["label"]["translated_value"] == "15N":
            ftcparams["15N_default_input_addon"] = {
                "translated_key": "15N_default_input_addon",
                "translated_value": '<note label="protein, modified residue mass file" type="input">{15N-masses}</note>'.format(
                    **ftcparams,
                ),
            }
        else:
            ftcparams["15N_default_input_addon"] = {
                "translated_key": "15N_default_input_addon",
                "translated_value": "<note "
                'label="protein, modified residue mass file" type="input">no</note>',
            }

        # Score ions
        for ion in ["a", "b", "c", "x", "y", "z"]:
            if ion in ftcparams["score_ion_list"]["translated_value"]:
                ftcparams[f"score_{ion}_ions"] = {
                    "translated_key": f"scoring, {ion} ions",
                    "translated_value": "yes",
                }
            else:
                ftcparams[f"score_{ion}_ions"] = {
                    "translated_key": f"scoring, {ion} ions",
                    "translated_value": "no",
                }
        return utrace

    def format_templates(
        self,
        utrace: urgap.UTrace,
    ) -> dict:
        """Create xtandem param files.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            Dict containing xtandem param files with respective content.
        """
        templates = {
            "15N-masses": """\
<?xml version="1.0"?>
    <bioml title="peptide residue molecular mass values for an all 15N organisms">
        <aa type="A" mass="72.034148698" />
        <aa type="B" mass="116.036998" />
        <aa type="C" mass="104.006219398" />
        <aa type="D" mass="116.023977958" />
        <aa type="E" mass="130.039628028" />
        <aa type="F" mass="148.065448838" />
        <aa type="G" mass="58.018498628" />
        <aa type="H" mass="140.050016555" />
        <aa type="I" mass="114.081098908" />
        <aa type="J" mass="0.0" />
        <aa type="K" mass="130.089032837" />
        <aa type="L" mass="114.081098908" />
        <aa type="M" mass="132.037519538" />
        <aa type="N" mass="116.036997257" />
        <aa type="O" mass="0.0" />
        <aa type="P" mass="98.049798768" />
        <aa type="Q" mass="130.052647327" />
        <aa type="R" mass="160.089250624" />
        <aa type="S" mass="88.029063328" />
        <aa type="T" mass="102.044713398" />
        <aa type="V" mass="100.065448838" />
        <aa type="W" mass="188.073382767" />
        <aa type="X" mass="112.057034" />
        <aa type="Y" mass="164.060363468" />
        <aa type="Z" mass="130.052648" />
        <molecule type="NH3" mass="18.02358311" />
        <molecule type="H2O" mass="18.01056470" />
    </bioml>
    """,
            # -------------------------
            # -------------------------
            "taxonomy": """<?xml version='1.0' encoding='iso-8859-1'?>
    <bioml label="x! taxon-to-file matching list">
      <taxon label="{database_taxonomy[translated_value]}">
       <file URL="{database[translated_value]}" format="peptide" />
     </taxon>
    </bioml>
    """.format(**utrace.urun_dict.translations["formatted_params"]),
            # -------------------------
            # -------------------------
            "input": """<?xml version='1.0' encoding='iso-8859-1'?>
    <bioml>
      <note label="list path, default parameters" type="input">{default_input[translated_value]}</note>
      <note label="list path, taxonomy information" type="input">{taxonomy[translated_value]}</note>
      <note label="spectrum, path" type="input">{mgf_input_file[translated_value]}</note>
      <note label="output, path" type="input">{output_file_incl_path[translated_value]}</note>
        </bioml>""".format(**utrace.urun_dict.translations["formatted_params"]),
            "default_input": """<?xml version='1.0' encoding='iso-8859-1'?>
    <bioml label="urgap">
    <note type="heading">

        Spectrum general

    </note>
    <note type="input" label="spectrum, parent monoisotopic mass error plus">{precursor_mass_tolerance_plus[translated_value]}</note>
    <note type="input" label="spectrum, parent monoisotopic mass error minus">{precursor_mass_tolerance_minus[translated_value]}</note>
    <note type="input" label="spectrum, parent monoisotopic mass error units">{precursor_mass_tolerance_unit[translated_value]}</note>
    <note type="input" label="spectrum, parent monoisotopic mass isotope error">{precursor_isotope_range[translated_value]}</note>
    <note type="input" label="spectrum, minimum parent m+h">{precursor_min_mass[translated_value]}</note>
    <note type="input" label="spectrum, fragment mass type">{frag_mass_type[translated_value]}</note>
    <note type="input" label="spectrum, fragment monoisotopic mass error">{frag_mass_tolerance[translated_value]}</note>
    <note type="input" label="spectrum, fragment monoisotopic mass error units">{frag_mass_tolerance_unit[translated_value]}</note>
    <note type="input" label="spectrum, fragment mass error">{frag_mass_tolerance[translated_value]}</note>
    <note type="input" label="spectrum, fragment mass error units">{frag_mass_tolerance_unit[translated_value]}</note>
    <note type="heading">

        Spectrum conditioning

    </note>
    <note type="input" label="spectrum, dynamic range">{spec_dynamic_range[translated_value]}</note>
    <note type="input" label="spectrum, total peaks">{max_accounted_observed_peaks[translated_value]}</note>
    <note type="input" label="spectrum, use noise suppression">{noise_suppression_enabled[translated_value]}</note>
    <note type="input" label="spectrum, use neutral loss window">{neutral_loss_enabled[translated_value]}</note>
    <note type="input" label="spectrum, neutral loss window">{neutral_loss_window[translated_value]}</note>
    <note type="input" label="spectrum, neutral loss mass">{neutral_loss_mass[translated_value]}</note>
    <note type="input" label="spectrum, minimum fragment mz">{frag_min_mz[translated_value]}</note>
    <note type="input" label="spectrum, minimum peaks">{min_required_observed_peaks[translated_value]}</note>
    <note type="input" label="spectrum, threads">{cpus[translated_value]}</note>
    <note type="input" label="spectrum, sequence batch size" >{batch_size[translated_value]}</note>
    <note type="input" label="spectrum, use noise suppression" >{noise_suppression_enabled[translated_value]}</note>
    <note type="heading">

        Residue modification

    </note>
    <note type="input" label="residue, modification mass">{fixed_modifications[translated_value]}</note>
    <note type="input" label="residue, potential modification mass">{potential_modifications[translated_value]}</note>
    <note type="heading">

        Protein general

    </note>
    <note type="input" label="protein, taxon">{database_taxonomy[translated_value]}</note>
    <note type="input" label="protein, cleavage site">{enzyme[translated_value]}</note>
    <note type="input" label="protein, cleavage C-terminal mass change">{cleavage_cterm_mass_change[translated_value]}</note>
    <note type="input" label="protein, cleavage N-terminal mass change">{cleavage_nterm_mass_change[translated_value]}</note>
    <note type="input" label="protein, cleavage semi">{enzyme_specificity[translated_value]}</note>
    <note type="input" label="protein, N-terminal residue modification mass">{Prot-N-term[translated_value]}</note>
    <note type="input" label="protein, C-terminal residue modification mass">{Prot-C-term[translated_value]}</note>
    <note type="input" label="protein, ptm complexity">{max_mod_alternatives[translated_value]}</note>
    <note type="input" label="protein, quick acetyl" >{acetyl_N_term[translated_value]}</note>
    <note type="input" label="protein, quick pyrolidone" >{pyro_glu[translated_value]}</note>
    <note type="input" label="protein, saps" >{search_for_saps[translated_value]}</note>
    <note type="input" label="protein, stP bias" >{xtandem_stp_bias[translated_value]}</note>
    {15N_default_input_addon[translated_value]}
    <note type="heading">

        Scoring

    </note>
    <note type="input" label="scoring, a ions">{score_a_ions[translated_value]}</note>
    <note type="input" label="scoring, b ions">{score_b_ions[translated_value]}</note>
    <note type="input" label="scoring, c ions" >{score_c_ions[translated_value]}</note>
    <note type="input" label="scoring, minimum ion count">{min_required_matched_peaks[translated_value]}</note>
    <note type="input" label="scoring, maximum missed cleavage sites">{max_missed_cleavages[translated_value]}</note>
    <note type="input" label="scoring, cyclic permutations" >{compensate_small_fasta[translated_value]}</note>
    <note type="input" label="scoring, include reverse" >{engine_internal_decoy_generation[translated_value]}</note>
    <note type="input" label="scoring, x ions" >{score_x_ions[translated_value]}</note>
    <note type="input" label="scoring, y ions" >{score_y_ions[translated_value]}</note>
    <note type="input" label="scoring, z ions" >{score_z_ions[translated_value]}</note>
    <note type="heading">

        Model refinement parameters

    </note>
    <note type="input" label="refine">{use_refinement[translated_value]}</note>
    <note type="input" label="refine, spectrum synthesis">no</note>
    <note type="input" label="refine, maximum valid expectation value">0.1</note>
    <note type="input" label="refine, potential N-terminus modifications"></note>
    <note type="input" label="refine, unanticipated cleavage">no</note>
    <note type="input" label="refine, potential modification mass">{refine_potential_modifications[translated_value]}</note>
    <note type="input" label="refine, use potential modifications for full refinement">no</note>
    <note type="input" label="refine, point mutations">no</note>
    <note type="heading">

        Output

    </note>
    <note type="input" label="output, path hashing">no</note>
    <note type="input" label="output, xsl path">tandem-style.xsl</note>
    <note type="input" label="output, parameters">yes</note>
    <note type="input" label="output, performance">yes</note>
    <note type="input" label="output, spectra">yes</note>
    <note type="input" label="output, histograms">yes</note>
    <note type="input" label="output, proteins">yes</note>
    <note type="input" label="output, sequences">yes</note>
    <note type="input" label="output, results">all</note>
    <note type="input" label="output, maximum valid expectation value">{max_output_e_value[translated_value]}</note>
    <note type="input" label="output, histogram column width">30</note>
    <note type="input" label="output, mzid">{output_file_type[translated_value]}</note>
        </bioml>""".format(**utrace.urun_dict.translations["formatted_params"]),
        }
        return templates
