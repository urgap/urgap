"""Urgap comet_2020_01_4 wrapper."""

import copy
import logging

try:
    from chemical_composition import chemical_composition_kb as cckb
except:
    pass
try:
    from unimod_mapper import UnimodMapper
except:
    pass

import urgap


class comet_2020_01_4(urgap.unode.UNodeBase):
    """Urgap wrapper for the comet_2020_01_4 search engine.

    Comet is an open-source MS/MS sequence database search tool. See publication
    provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "comet_2020_01_4",
        "version": "2020.01.4",
        "release_date": "11.05.2021",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "api_port": 42701,
        "engine_type": ("db_search", "proteomics"),
        "platform_independent": False,
        "utranslation_style": "comet_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "comet.exe",
                    "uri": None,
                    "urn": "darwin/arm64/comet_2020_01_4.zip",
                    "urn_md5": "a4a9f1959ae16a16510619da976dfcb3",
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "comet.exe",
                    "uri": None,
                    "urn": "darwin/x86_64/comet_2020_01_4.zip",
                    "urn_md5": "a4a9f1959ae16a16510619da976dfcb3",
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "linux": {
                "arm64": {
                    "exe": "comet.exe",
                    "uri": None,
                    "urn": "linux/arm64/comet_2020_01_4.zip",
                    "urn_md5": "878a51d92061371c88f04890d03c1e56",
                    "external_md5": None,
                    "external_url": None,
                },
                "x86_64": {
                    "exe": "comet.exe",
                    "uri": None,
                    "urn": "linux/x86_64/comet_2020_01_4.zip",
                    "urn_md5": "878a51d92061371c88f04890d03c1e56",
                    "external_md5": None,
                    "external_url": None,
                },
            },
            "win32": {
                "x86_64": {
                    "exe": "comet.exe",
                    "uri": None,
                    "urn": "win32/x86_64/comet_2020_01_4.zip",
                    "urn_md5": "a161bf76dadd19847739cb42dfa1d2a6",
                    "external_url": None,
                    "external_md5": None,
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "chemical_composition",
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
            urgap.uftypes.proteomics.dbsearch.COMET_MZID: {"min": 1, "max": 1},
        },
        "citation": """
        Eng, J. K., Jahan, T. A., & Hoopmann, M. R. (2012). Comet: An open-source MS/MS sequence database search tool.
        In PROTEOMICS (Vol. 13, Issue 1, pp. 22-24). Wiley. https://doi.org/10.1002/pmic.201200439
        """,
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize comet_2020_01_4 class."""
        super().__init__(*args, **kwargs)

    def format_params(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Format params into a format expected by the comet search engine.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            formatted_fix_dict (dict): dict with formatted fixed modes in comet suitable
                format
        """
        utrace.urun_dict.translations["formatted_params"] = copy.deepcopy(
            utrace.urun_dict.translations["all_params"],
        )
        ftcparams = utrace.urun_dict.translations["formatted_params"]

        # Format the score ions
        for ion in ["a", "b", "c", "x", "y", "z", "z1", "nl"]:
            value = 0
            if ion in ftcparams["score_ion_list"]["translated_value"]:
                value = 1
            ftcparams[f"score_{ion.upper()}_ions"] = {
                "translated_key": f"score_{ion.upper()}_ions",
                "translated_value": value,
            }

        _comet_precursor_error = (
            float(ftcparams["precursor_mass_tolerance_minus"]["translated_value"])
            + float(ftcparams["precursor_mass_tolerance_plus"]["translated_value"])
        ) / 2.0
        ftcparams["peptide_mass_tolerance"] = {
            "translated_key": "peptide_mass_tolerance",
            "translated_value": _comet_precursor_error,
        }

        print(
            """
            [ WARNING ] precursor_mass_tolerance_plus and precursor_mass_tolerance_minus
            [ WARNING ] need to be combined for Comet (use of symmetric tolerance window).
            [ WARNING ] The arithmetic mean is used.
            """,
        )

        # Format the charge range
        min_charge = int(ftcparams["precursor_min_charge"]["translated_value"])
        max_charge = int(ftcparams["precursor_max_charge"]["translated_value"])
        ftcparams["precursor_charge"] = {
            "translated_key": "precursor_charge",
            "translated_value": f"{min_charge} {max_charge}",
        }

        # Format the peptide length range
        min_length = int(ftcparams["min_pep_length"]["translated_value"])
        max_length = int(ftcparams["max_pep_length"]["translated_value"])
        ftcparams["peptide_length_range"] = {
            "translated_key": "peptide_length_range",
            "translated_value": f"{min_length} {max_length}",
        }

        # Format the digest mass range
        min_precursor_mass = int(ftcparams["precursor_min_mass"]["translated_value"])
        max_precursor_mass = int(ftcparams["precursor_max_mass"]["translated_value"])
        ftcparams["digest_mass_range"] = {
            "translated_key": "digest_mass_range",
            "translated_value": f"{min_precursor_mass} {max_precursor_mass}",
        }

        # # Removed the output suffix from params as it is set by urgap2!
        # output_suffix = self.META_INFO.get("output_suffix", "")
        # ftcparams["output_suffix"] = {
        #     "translated_key": "output_suffix",
        #     "translated_value": output_suffix,
        # }

        # format the mass_offset_list to a str for comet
        mass_offset_list = ftcparams["mass_offset_list"]["translated_value"]
        ftcparams["mass_offset_list"]["translated_value"] = " ".join(mass_offset_list)

        # format the output_mzidentmlfile based on output_file_extension
        # Commented out until we discussed how output file types should be implemented
        # if self.META_INFO["output_file_extension"] != ".mzid":
        #     ftcparams["export_mzidentmlfile"] = {
        #         "translated_key": "output_mzidentmlfile",
        #         "translated_value": 0,
        #     }

        # format the precursor_NL_ions list to a str for comet
        if ftcparams["precursor_nl_ions"]["translated_value"] == []:
            ftcparams["precursor_nl_ions"]["translated_value"] = ""

        # format the peff_obo_path so it is ignored if not defined
        if ftcparams["peff_obo_path"]["translated_value"] is None:
            ftcparams["peff_obo_path"]["translated_value"] = 0

        # format the scan_inclusion_list
        if ftcparams["scan_inclusion_list"]["translated_value"] is None:
            ftcparams["scan_inclusion_list"]["translated_value"] = "0 0"

        # format range lists to range strings for comet
        ftcparams["frag_clear_mz_range"]["translated_value"] = " ".join(
            map(str, ftcparams["frag_clear_mz_range"]["translated_value"]),
        )

        # strip the file extension from output_filename as comet sets it by itself and
        # otherwise the file will be output.extension.extension...
        ftcparams["output_file_wo_ext"] = (
            f"{utrace.output_files[0].path.parent}/{utrace.output_files[0].path.stem}"
        )
        fasta_file = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.FASTA,
        )[0]
        ftcparams["database"]["translated_value"] = str(fasta_file)
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for comet_2020_01_4 wrapper.

        During preflight,
            - parameters are formatted
            - mods are mapped and formatted
            - param file is written
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

        ftcparams = utrace.urun_dict.translations["formatted_params"]
        ftcparams.update(self.format_opt_mods())
        ftcparams.update(self.format_fix_mods())

        self.write_param_file(utrace=utrace)

        mgf_file = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.proteomics.converter.PYMZML_MGF,
        )[0]

        utrace.urun_dict.command_list = [
            f"{self.exe_path}",
            f"-P{ftcparams['param_file']}",
            f"-N{ftcparams['output_file_wo_ext']}",
            str(mgf_file),
        ]
        return utrace

    def format_opt_mods(self) -> dict:
        """Format opt mods into proper style, which is printed into the params template and used by the comet search.

        Returns:
            Dict with formatted opts mods in comet format.
        """
        # TODO: check if it is required to merge the mod if same mod occurs
        #  at different aa

        opt_mods = self.mapped_mods["opt"]
        variable_mods_string = ""
        for n, mod in enumerate(opt_mods, 1):
            pos_01 = mod["mass"]
            pos_02 = ""
            pos_03 = 0
            pos_04 = 3  # default value of comet
            pos_05 = -1  # create a new similar to 143
            pos_06 = 0  # from the mod string? - only for prot n/c term
            pos_07 = 0  # from the mod string?
            pos_08 = 0.0  # get out the NL from unimod_mapper

            if mod["aa"] in cckb.aa_names:
                pos_02 = mod["aa"]
            elif mod["aa"] == "*":
                pass
            else:
                raise SyntaxError("Expected '*' or valid aa in one letter code!")

            if mod["position"] == "Prot-N-term":
                pos_02 = "n" + pos_02
                pos_06 = 0
            elif mod["position"] == "Prot-C-term":
                pos_02 = "c" + pos_02
                pos_06 = 1
            elif mod["position"] == "N-term":
                pos_02 = "n" + pos_02
                pos_06 = 2
            elif mod["position"] == "C-term":
                pos_02 = "c" + pos_02
                pos_06 = 3

            if mod.get("max_num_per_peptide", None) is not None:
                if len(mod["max_num_per_peptide"]) == 1:
                    pos_04 = mod["max_num_per_peptide"][0]
                elif len(mod["max_num_per_peptide"]) == 2:
                    pos_04 = ",".join(str(x) for x in mod["max_num_per_peptide"])
                else:
                    logging.warning("Comet only accepts only a list of 1 or 2 values!")

            if mod.get("intern_dist", None) is not None:
                pos_05 = mod["intern_dist"]

            if mod.get("required", None) is not None:
                pos_07 = mod["required"]

            if mod.get("neutral_loss", None) is not None:
                pos_08 = mod["neutral_loss"]

            formatted_opt_mod = (
                f"variable_mod{str(n).zfill(2)} = {pos_01} {pos_02} "
                f"{pos_03} {pos_04} {pos_05} {pos_06} {pos_07} {pos_08}\n"
            )
            variable_mods_string += formatted_opt_mod
            formatted_opts_dict = {"opt": variable_mods_string}
        return formatted_opts_dict

    def format_fix_mods(self) -> dict:
        """Format fixed mods into proper style, which is printed into the params template and used by the comet search.

        Returns:
            Dict with formatted fixed mods in comet format.
        """
        mod_string = ""
        formatted_fix_dict = {"fix": ""}
        for mod in self.mapped_mods["fix"]:
            if mod["aa"] in cckb.aa_names:
                sl_aa = mod["aa"]  # sl = single letter
                fn_aa = cckb.aa_names[sl_aa]  # fn = full name
                formatted_fix_mod = f"add_{sl_aa}_{fn_aa} = {mod['mass']}\n"
            elif mod["aa"] == "*":
                if mod["position"] == "Prot-N-term":
                    formatted_fix_mod = f"add_Nterm_protein = {mod['mass']}\n"
                elif mod["position"] == "Prot-C-term":
                    formatted_fix_mod = f"add_Cterm_protein = {mod['mass']}\n"

            mod_string += formatted_fix_mod
            formatted_fix_dict = {"fix": mod_string}
        return formatted_fix_dict

    def format_param_file(
        self,
        utrace: urgap.UTrace,
    ) -> str:
        """Create a comet.params file.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta - to be written out.

        Returns:
            Template string.
        """
        template = """
# comet_version 2020.01 rev. 4
# Comet MS/MS search engine parameters file.
# Everything following the '#' symbol is treated as a comment.

database_name = {database[translated_value]}
decoy_search = {engine_internal_decoy_generation[translated_value]}                       # 0=no (default), 1=concatenated search, 2=separate search
peff_format = {database_format[translated_value]}                        # 0=no (normal fasta, default), 1=PEFF PSI-MOD, 2=PEFF Unimod
peff_obo = {peff_obo_path[translated_value]}                            # path to PSI Mod or Unimod OBO file

num_threads = {cpus[translated_value]}                        # 0=poll CPU to set num threads; else specify num threads directly (max 128)

#
# masses
#
peptide_mass_tolerance = {peptide_mass_tolerance[translated_value]}
peptide_mass_units = {precursor_mass_tolerance_unit[translated_value]}                  # 0=amu, 1=mmu, 2=ppm
mass_type_parent = {precursor_mass_type[translated_value]}                    # 0=average masses, 1=monoisotopic masses
mass_type_fragment = {frag_mass_type[translated_value]}                  # 0=average masses, 1=monoisotopic masses
precursor_tolerance_type = {precursor_tolerance_type[translated_value]}            # 0=MH+ (default), 1=precursor m/z; only valid for amu/mmu tolerances
isotope_error = {precursor_isotope_range[translated_value]}                       # 0=off, 1=0/1 (C13 error), 2=0/1/2, 3=0/1/2/3, 4=-8/-4/0/4/8 (for +4/+8 labeling)

#
# search enzyme
#
search_enzyme_number = {enzyme[translated_value]}               # choose from list at end of this params file
search_enzyme2_number = 0              # second enzyme; set to 0 if no second enzyme
num_enzyme_termini = {enzyme_specificity[translated_value]}                 # 1 (semi-digested), 2 (fully digested, default), 8 C-term unspecific , 9 N-term unspecific
allowed_missed_cleavage = {max_missed_cleavages[translated_value]}            # maximum value is 5; for enzyme search

#
# Up to 9 variable modifications are supported
# format:  <mass> <residues> <0=variable/else binary> <max_mods_per_peptide> <term_distance> <n/c-term> <required> <neutral_loss>
#     e.g. 79.966331 STY 0 3 -1 0 0 97.976896
#
{opt}
max_variable_mods_in_peptide = {max_num_mods[translated_value]}
require_variable_mod = {require_variable_mod[translated_value]}

#
# fragment ions
#
# ion trap ms/ms:  1.0005 tolerance, 0.4 offset (mono masses), theoretical_fragment_ions = 1
# high res ms/ms:    0.02 tolerance, 0.0 offset (mono masses), theoretical_fragment_ions = 0, spectrum_batch_size = 15000
#
fragment_bin_tol = {fragment_bin_size[translated_value]}              # binning to use on fragment ions
fragment_bin_offset = {fragment_bin_offset[translated_value]}              # offset position to start the binning (0.0 to 1.0)
theoretical_fragment_ions = {theoretical_fragment_ions[translated_value]}          # 0=use flanking peaks, 1=M peak only
use_A_ions = {score_A_ions[translated_value]}
use_B_ions = {score_B_ions[translated_value]}
use_C_ions = {score_C_ions[translated_value]}
use_X_ions = {score_X_ions[translated_value]}
use_Y_ions = {score_Y_ions[translated_value]}
use_Z_ions = {score_Z_ions[translated_value]}
use_Z1_ions = {score_Z1_ions[translated_value]}
use_NL_ions = {score_NL_ions[translated_value]}                        # 0=no, 1=yes to consider NH3/H2O neutral loss peaks

#
# output
#
output_sqtfile = 0                     # 0=no, 1=yes  write sqt file
output_txtfile = 0                     # 0=no, 1=yes  write tab-delimited txt file
output_pepxmlfile = {export_pepxml[translated_value]}                  # 0=no, 1=yes  write pepXML file
output_mzidentmlfile = 1                  # 0=no, 1=yes  write mzIdentML file
output_percolatorfile = {export_percolator[translated_value]}              # 0=no, 1=yes  write Percolator pin file
print_expect_score = {print_expect_score[translated_value]}                 # 0=no, 1=yes to replace Sp with expect in out & sqt
num_output_lines = {num_match_spec[translated_value]}                   # num peptide results to show

sample_enzyme_number = {sample_enzyme[translated_value]}               # Sample enzyme which is possibly different than the one applied to the search.
                                                                       # Used to calculate NTT & NMC in pepXML output (default=1 for trypsin).

#
# mzXML parameters
#
scan_range = {scan_inclusion_list[translated_value]}                       # start and end scan range to search; either entry can be set independently
precursor_charge = {precursor_charge[translated_value]}                 # precursor charge range to analyze; does not override any existing charge; 0 as 1st entry ignores parameter
override_charge = {use_spectrum_charge[translated_value]}                    # 0=no, 1=override precursor charge states, 2=ignore precursor charges outside precursor_charge range, 3=see online
ms_level = {ms_level[translated_value]}                           # MS level to analyze, valid are levels 2 (default) or 3
activation_method = {frag_method[translated_value]}                # activation method; used if activation method set; allowed ALL, CID, ECD, ETD, ETD+SA, PQD, HCD, IRMPD, SID

#
# misc parameters
#
digest_mass_range = {digest_mass_range[translated_value]}       # MH+ peptide mass range to analyze
peptide_length_range = {peptide_length_range[translated_value]}            # minimum and maximum peptide length to analyze (default 1 63; max length 63)
num_results = {num_results[translated_value]}                      # number of search hits to store internally
max_duplicate_proteins = {max_duplicate_proteins[translated_value]}            # maximum number of additional duplicate protein names to report for each peptide ID; -1 reports all duplicates
max_fragment_charge = {frag_max_charge[translated_value]}                # set maximum fragment charge state to analyze (allowed max 5)
max_precursor_charge = {precursor_max_charge[translated_value]}               # set maximum precursor charge state to analyze (allowed max 9)
nucleotide_reading_frame = {nucleotide_reading_frame[translated_value]}           # 0=proteinDB, 1-6, 7=forward three, 8=reverse three, 9=all six
clip_nterm_methionine = {clip_nterm_m[translated_value]}              # 0=leave sequences as-is; 1=also consider sequence w/o N-term methionine
spectrum_batch_size = {batch_size_spectra[translated_value]}            # max. # of spectra to search at a time; 0 to search the entire scan range in one loop
decoy_prefix = {decoy_tag[translated_value]}                  # decoy entries are denoted by this string which is pre-pended to each protein accession
equal_I_and_L = {equal_isoleucin_leucin[translated_value]}                      # 0=treat I and L as different; 1=treat I and L as same
output_suffix =                        # add a suffix to output base names i.e. suffix "-C" generates base-C.pep.xml from base.mzXML input
mass_offsets = {mass_offset_list[translated_value]}                        # one or more mass offsets to search (values substracted from deconvoluted precursor mass)
precursor_NL_ions = {precursor_nl_ions[translated_value]}                      # one
or more precursor neutral loss masses, will be added to xcorr analysis
peff_verbose_output = {verbose_behavior[translated_value]}
skip_researching = 1
text_file_extension =                   # add another text file extension if required
explicit_deltacn = {explicit_deltacn[translated_value]}


#
# spectral processing
#
minimum_peaks = {min_required_observed_peaks[translated_value]}                     # required minimum number of peaks in spectrum to search (default 10)
minimum_intensity = {minimum_intensity[translated_value]}                  # minimum intensity value to read in
remove_precursor_peak = {remove_precursor_peak[translated_value]}              # 0=no, 1=yes, 2=all charge reduced precursor peaks (for ETD), 3=phosphate neutral loss peaks
remove_precursor_tolerance = {remove_precursor_tolerance[translated_value]}       # +- Da tolerance for precursor removal
clear_mz_range = {frag_clear_mz_range[translated_value]}               # for iTRAQ/TMT type data; will clear out all peaks in the specified m/z range

#
# additional modifications
#
{fix}

#
# COMET_ENZYME_INFO _must_ be at the end of this parameters file
#
[COMET_ENZYME_INFO]
0.  Cut_everywhere         0      -           -
1.  Trypsin                1      KR          P
2.  Trypsin/P              1      KR          -
3.  Lys_C                  1      K           P
4.  Lys_N                  0      K           -
5.  Arg_C                  1      R           P
6.  Asp_N                  0      D           -
7.  CNBr                   1      M           -
8.  Glu_C                  1      DE          P
9.  PepsinA                1      FL          P
10. Chymotrypsin           1      FWYL        P

        """.format(**utrace.urun_dict.translations["formatted_params"])
        return template

    def write_param_file(
        self,
        utrace: urgap.UTrace,
    ):
        """Write out the param file used by the search engine.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta - to be written out.
        """
        param_template = self.format_param_file(utrace=utrace)
        param_file = f"{utrace.output_files[0].path}_params.txt"
        utrace.urun_dict.translations["formatted_params"]["param_file"] = param_file
        with open(param_file, "w") as out:
            print(param_template, file=out)
