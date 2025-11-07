"""Urgap msamanda_2_0_0_17442 wrapper."""

import copy
import logging
import os
import time

try:
    from unimod_mapper.unimod_mapper import UnimodMapper
except:
    pass

import urgap


class msamanda_2_0_0_17442(urgap.unode.UNodeBase):
    """Urgap wrapper for the msamanda_2_0_0_17442 search engine.

    MS Amanda is a database search engine, specially developed for high-resolution
    tandem mass spectrometry data, taking advantage of high mass accuracy and
    considering fragment ion intensities. See publication provided under META_INFO[
    "citation"] for further info.
    """

    META_INFO = {
        "name": "msamanda_2_0_0_17442",
        "version": "2.0.0.17442",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "22.04.2021",
        "api_port": 42709,
        "engine_type": ("db_search", "proteomics"),
        "platform_independent": False,
        "utranslation_style": "msamanda_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "MSAmanda",
                    "uri": None,
                    "urn": "darwin/arm64/msamanda_2_0_0_17442.zip",
                    "urn_md5": "982a00c37104690c11ba60929e094d09",
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "MSAmanda",
                    "uri": None,
                    "urn": "darwin/x86_64/msamanda_2_0_0_17442.zip",
                    "urn_md5": "982a00c37104690c11ba60929e094d09",
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "linux": {
                "arm64": {
                    "exe": "MSAmanda",
                    "uri": None,
                    "urn": "linux/arm64/msamanda_2_0_0_17442.zip",
                    "urn_md5": "97d21103177afcd7f2480da1d1585c59",
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "MSAmanda",
                    "uri": None,
                    "urn": "linux/x86_64/msamanda_2_0_0_17442.zip",
                    "urn_md5": "97d21103177afcd7f2480da1d1585c59",
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
            urgap.uftypes.proteomics.dbsearch.MSAMANDA_CSV: {"min": 1, "max": 1},
        },
        "citation": """
        Dorfer, V., Pichler, P., Stranzl, T., Stadlmann, J., Taus, T., Winkler, S., & Mechtler, K. (2014). MS Amanda, a Universal Identification Algorithm Optimized for High Accuracy Tandem Mass Spectra.
        In Journal of Proteome Research (Vol. 13, Issue 8, pp. 3679-3684). American Chemical Society (ACS). https://doi.org/10.1021/pr500202e
        """,
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize msamanda_2_0_0_17442 class."""
        super().__init__(*args, **kwargs)

    def format_params(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Format params into a format expected by the msamanda search engine.

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
            uftype=urgap.uftypes.proteomics.converter.PYMZML_MGF,
        )[0]
        ftcparams["mgf_input_file"]["translated_value"] = str(mgf_file)

        ftcparams["output_file_incl_path"]["translated_value"] = (
            f"{utrace.output_files[0].path}"
        )

        # Unimod.xml file will be taken from unimod_mapper. The first element of the
        # list is the usermod.xml which will be ifnored for now
        ftcparams["unimod_file_incl_path"] = {
            "translated_key": "unimod_file",
            "translated_value": f"{UnimodMapper().unimod_xml_names[1]}",
        }

        fasta_file = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.FASTA,
        )[0]
        ftcparams["database"]["translated_value"] = str(fasta_file)

        score_ions = []
        instruments_file_input = []
        for ion in [
            "a",
            "b",
            "c",
            "x",
            "y",
            "z",
            "-H2O",
            "-NH3",
            "Imm",
            "z+1",
            "z+2",
            "INT",
        ]:
            if ion.lower() in ftcparams["score_ion_list"]["translated_value"]:
                score_ions.append(ion)
                instruments_file_input.append(f"""<series>{ion}</series>""")
        instruments_file_input.append("""</setting>""")
        instruments_file_input.append("""</instruments>""")
        ftcparams["score_ions"] = {
            "translated_key": "score_ions",
            "translated_value": ", ".join(score_ions),
        }

        ftcparams["instruments_file_input"] = {
            "translated_key": "instruments_file_input",
            "translated_value": "".join(instruments_file_input),
        }

        _msamanda_precursor_error = (
            float(ftcparams["precursor_mass_tolerance_minus"]["translated_value"])
            + float(ftcparams["precursor_mass_tolerance_plus"]["translated_value"])
        ) / 2.0
        ftcparams["precursor_mass_tolerance"] = {
            "translated_key": "ms1_tol",
            "translated_value": _msamanda_precursor_error,
        }

        print(
            """
            [ WARNING ] precursor_mass_tolerance_plus and precursor_mass_tolerance_minus
            [ WARNING ] need to be combined for MS Amanda (use of symmetric tolerance window).
            [ WARNING ] The arithmetic mean is used.
            """,
        )

        considered_charges = []
        for charge in range(
            int(ftcparams["precursor_min_charge"]["translated_value"]),
            int(ftcparams["precursor_max_charge"]["translated_value"]) + 1,
        ):
            considered_charges.append(f"{charge}+")

        ftcparams["considered_charges"] = {
            "translated_key": "considered_charges",
            "translated_value": ", ".join(considered_charges),
        }

        (
            ftcparams["enzyme_cleavage"],
            ftcparams["enzyme_position"],
            ftcparams["enzyme_inhibitors"],
        ) = ftcparams["enzyme"]["translated_value"].split(";")
        return utrace

    def write_templates(
        self,
        utrace: urgap.UTrace,
    ):
        """Write templates - param files required by msamanda search engine.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
        """
        templates = self.format_templates(utrace=utrace)
        for file_name, content in templates.items():
            file2write = f"{utrace.output_files[0].path}{file_name}"
            if os.path.exists(file2write):
                file2write = file2write.replace(".xml", f"{time.time()}.xml")
            with open(file2write, "w") as out:
                print(content, file=out)
                msg = f"Wrote input file {file2write}"
                logging.info(msg)
                self.tmp_files.append(file2write)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for msamanda_2_0_0_17442 wrapper.

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
        utrace.urun_dict.translations["formatted_params"].update(self.format_mods())
        self.write_templates(utrace=utrace)

        mgf = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.converter.PYMZML_MGF,
        )[0]
        fasta = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.FASTA,
        )[0]
        fasta_suffix = ".fasta"
        if fasta.suffix != fasta_suffix:
            if fasta.with_suffix(fasta_suffix).exists():
                if os.readlink(fasta.with_suffix(fasta_suffix)) != str(fasta):
                    msg = f"Symlink of fasta {fasta} pointing to wrong target."
                    logging.error(msg)
            else:
                os.symlink(src=fasta, dst=fasta.with_suffix(fasta_suffix))
        # building command_list !
        utrace.urun_dict.command_list = [
            f"{self.exe_path}",
            "-s",
            str(mgf),
            "-d",
            str(fasta.with_suffix(fasta_suffix)),
            "-e",
            str(utrace.output_files[0].path) + "_settings.xml",
            "-o",
            str(utrace.output_files[0].path),
        ]
        return utrace

    def format_templates(
        self,
        utrace: urgap.UTrace,
    ) -> dict:
        """Create msamanda param files.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            Dict containing msmamanda param files with respective content.
        """
        templates = {
            "_settings.xml": """<?xml version="1.0" encoding="utf-8" ?>
<settings>
<search_settings>
    <enzyme specificity="{enzyme_specificity[translated_value]}">{enzyme[original_value]}</enzyme>
    <missed_cleavages>{max_missed_cleavages[translated_value]}</missed_cleavages>
    <modifications>
        {fix}{opt}
    </modifications>
    <instrument>{score_ions[translated_value]}</instrument>
    <ms1_tol unit="{precursor_mass_tolerance_unit[translated_value]}">{precursor_mass_tolerance[translated_value]}</ms1_tol>
    <ms2_tol unit="{frag_mass_tolerance_unit[translated_value]}">{frag_mass_tolerance[translated_value]}</ms2_tol>
    <max_rank>{num_match_spec[translated_value]}</max_rank>
    <generate_decoy>{engine_internal_decoy_generation[translated_value]}</generate_decoy>
    <PerformDeisotoping>{deisotope_spec[translated_value]}</PerformDeisotoping>
    <MaxNoModifs>{max_num_per_mod[translated_value]}</MaxNoModifs>
    <MaxNoDynModifs>{max_num_mods[translated_value]}</MaxNoDynModifs>
    <MaxNumberModSites>{max_num_mod_sites[translated_value]}</MaxNumberModSites>
    <MaxNumberNeutralLoss>{max_num_neutral_loss[translated_value]}</MaxNumberNeutralLoss>
    <MaxNumberNeutralLossModifications>{max_num_neutral_loss_mod[translated_value]}</MaxNumberNeutralLossModifications>
    <MinimumPepLength>{min_pep_length[translated_value]}</MinimumPepLength>
    <MaximumPepLength>{max_pep_length[translated_value]}</MaximumPepLength>
    <!-- added from default settings.xml as not present in uparma atm -->
    <!-- false -> combine ranks for target and decoy, true -> own rankings for target and decoy -->
    <ReportBothBestHitsForTD>false</ReportBothBestHitsForTD>
</search_settings>

<basic_settings>
<instruments_file>{output_file_incl_path[translated_value]}_instrument.xml</instruments_file>
<unimod_file>{unimod_file_incl_path[translated_value]}</unimod_file>
<enzyme_file>{output_file_incl_path[translated_value]}_enzymes.xml</enzyme_file>
<monoisotopic>{precursor_mass_type[translated_value]}</monoisotopic>
<considered_charges>{considered_charges[translated_value]}</considered_charges>
<!-- added from default settings.xml as not present in uparma atm -->
<!-- default true -> considered charges are combined in one result -->
<combine_considered_charges>true</combine_considered_charges>
<LoadedProteinsAtOnce>{batch_size[translated_value]}</LoadedProteinsAtOnce>
<LoadedSpectraAtOnce>{batch_size_spectra[translated_value]}</LoadedSpectraAtOnce>
</basic_settings>
</settings>
""".format(**utrace.urun_dict.translations["formatted_params"]),
            "_instrument.xml": """<?xml version="1.0"?>
<!-- possible values are "a", "b", "c", "x", "y", "z", "H2O", "NH3", "IMM", "z+1", "z+2", "INT" (for internal fragments) -->
<instruments>
<setting name="{score_ions[translated_value]}">
{instruments_file_input[translated_value]}
""".format(**utrace.urun_dict.translations["formatted_params"]),
            "_enzymes.xml": """<?xml version="1.0" encoding="utf-8" ?>
<enzymes>
<enzyme>
<name>{enzyme[original_value]}</name>
<cleavage_sites>{enzyme_cleavage}</cleavage_sites>
<inhibitors>{enzyme_inhibitors}</inhibitors>
<position>{enzyme_position}</position>
</enzyme>
    </enzymes>""".format(**utrace.urun_dict.translations["formatted_params"]),
        }
        return templates

    def format_mods(self) -> dict:
        """Format mods into proper style, which is printed into the params template and used by the msamanda search.

        Returns:
            Dict with formatted mods in msamanda format.
        """
        # if udict["formatted_translated_cparameters"]["label"]["translated_value"] == " \
        #                                                       ""15N":
        #     for aminoacid in cckb.aa_compositions.keys():
        #         existing = False
        #         for mod in udict["mapped_mods"]["fix"]:
        #             if aminoacid == mod["aa"]:
        #                 mod["mass"] += cckb.calculate_N_difference(aminoacid)
        #                 mod["name"] += "_15N_{0}".format(aminoacid)
        #                 existing = True
        #         if existing == True:
        #             continue
        #         udict["mapped_mods"]["fix"].append(
        #             {
        #                 "pos": "any",
        #                 "aa": aminoacid,
        #                 "name": "15N_{0}".format(aminoacid),
        #                 "mass": N15_Diff,
        #             }
        #         )

        tmp_dict = {}
        for mod_type in ["fix", "opt"]:
            modifications = []
            tmp_dict[mod_type] = ""
            fix = "false"
            if mod_type == "fix":
                fix = "true"
            for mod in self.mapped_mods[mod_type]:
                protein = "false"
                n_term = "false"
                c_term = "false"
                if ">" in mod["name"]:
                    print(
                        """
                        [ WARNING ] MS Amanda cannot deal with '>'
                        [ WARNING ] in the modification name
                        [ WARNING ] Continue without modification {} """.format(
                            mod,
                            **mod,
                        ),
                    )
                    continue
                if "Prot" in mod["position"]:
                    protein = "true"
                if "N-term" in mod["position"]:
                    n_term = "true"
                if "C-term" in mod["position"]:
                    c_term = "true"
                if "*" in mod["aa"]:
                    modifications.append(
                        '<modification fix="{}" protein="{}" nterm="{}" cterm="{}" delta_mass="{}">{}</modification>'.format(
                            fix,
                            protein,
                            n_term,
                            c_term,
                            mod["mass"],
                            mod["name"],
                        ),
                    )
                else:
                    modifications.append(
                        '<modification fix="{}" protein="{}" nterm="{}" cterm="{}" delta_mass="{}">{}({})</modification>'.format(
                            fix,
                            protein,
                            n_term,
                            c_term,
                            mod["mass"],
                            mod["name"],
                            mod["aa"],
                        ),
                    )
                tmp_dict[mod_type] = "".join(modifications)
        return tmp_dict
