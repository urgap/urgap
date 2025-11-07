"""Urgap msfragger_3 wrapper."""

import logging
import os

from collections import defaultdict as ddict

try:
    from chemical_composition import ChemicalComposition, chemical_composition_kb
except:
    pass
try:
    from unimod_mapper import UnimodMapper
except:
    pass

import urgap


class msfragger_3(urgap.unode.UNodeBase):
    """Urgap wrapper for the msfragger_3 search engine.

    MSFragger is an ultrafast database search tool for peptide identification in mass
    spectrometry-based proteomics. See publication provided under META_INFO[
    "citation"] for further info.
    """

    META_INFO = {
        "name": "msfragger_3",
        "version": "0.0.1",
        "release_date": "03.05.2021",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "api_port": 42710,
        "engine_type": ("db_search", "open_search", "proteomics"),
        "platform_independent": True,
        "requires": {
            "other_uftypes": {
                "other_dependencies": ("java",),
                "python_packages": [
                    "chemical_composition",
                    "unimod_mapper",
                ],
            },
        },
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "MSFragger-3.0.jar",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/msfragger_3.zip",
                    "urn_md5": "3ba624056c15a7fddadd3286166f7b03",
                    "additional_exe": {},
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.converter.PYMZML_MGF: {"min": 1, "max": 1},
            urgap.uftypes.proteomics.MODS_XML: {"min": 0, "max": -1},
            urgap.uftypes.proteomics.FASTA: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.dbsearch.MSFRAGGER_TSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "msfragger_style_3",
        "citation": """
        Kong, A. T., Leprevost, F. V., Avtonomov, D. M., Mellacheruvu, D., & Nesvizhskii, A. I. (2017). MSFragger: ultrafast and comprehensive peptide identification in mass spectrometry-based proteomics.
        In Nature Methods (Vol. 14, Issue 5, pp. 513-520). Springer Science and Business Media LLC. https://doi.org/10.1038/nmeth.4256
        """,
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize msfragger_3 class."""
        super().__init__(*args, **kwargs)

    def write_param_file(
        self,
        utrace: urgap.UTrace,
    ) -> os.PathLike:
        """Write msfragger parameter file.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            Path of the parameter file.
        """
        self.mass_glycan_lookup = {}
        self.mass_shift_lookup = {}

        write_exclusion_list = [
            "precursor_min_mass",
            "precursor_max_mass",
            "precursor_min_charge",
            "precursor_max_charge",
            "label",
            "-xmx",
            "header_translations",
            "validation_score_field",
            "database",
        ]
        msfragger_param_path = utrace.output_files[0].path.parent / "msfragger.params"
        with open(msfragger_param_path, "w") as fh:
            for param_key, param_value in sorted(
                utrace.urun_dict.translations["all_params"].items(),
                key=lambda x: x[0].lower(),
            ):
                if param_key in write_exclusion_list:
                    continue
                translated_key = param_value["translated_key"]
                if param_key == "frag_clear_mz_range":
                    min_mz, max_mz = param_value["translated_value"]
                    print(f"{translated_key:30} = {min_mz} {max_mz}", file=fh)
                elif param_key == "decoy_tag":
                    if "#" in param_value["translated_value"]:
                        raise ValueError(
                            "MSFragger does not accept fasta files containing # as decoy tag",
                        )
                elif param_key == "enzyme":
                    search_enzyme_name = param_value["original_value"]
                    aa_site, _, inhibitor = param_value["translated_value"].split(";")
                    print(f"search_enzyme_name = {search_enzyme_name}", file=fh)
                    print(f"search_enzyme_cutafter = {aa_site}", file=fh)
                    print(f"search_enzyme_butnotafter = {inhibitor}", file=fh)
                elif param_key == "enzyme_specificity":
                    num_enzyme_termini = (
                        0
                        if utrace.urun_dict.translations["all_params"]["enzyme"][
                            "original_value"
                        ]
                        == "nonspecific"
                        else param_value["translated_value"]
                    )
                    print(f"{translated_key:30} = {num_enzyme_termini}", file=fh)
                elif param_key == "precursor_mass_tolerance_minus":
                    param_value = param_value["translated_value"]
                    param_value *= -1
                    print(f"{translated_key:30} = {param_value}", file=fh)
                elif param_key == "diagnostic_fragments":
                    formatted_params = self.format_diagnostic_fragments(
                        param_value["translated_value"],
                    )
                    print(f"{translated_key:30} = {formatted_params}", file=fh)
                elif param_key == "modifications":
                    if len(self.mapped_mods["fix"] + self.mapped_mods["opt"]) != 0:
                        formatted_mods = self.format_mods(self.mapped_mods)
                    else:
                        formatted_mods = {}
                    # we write the mods at the very end :)
                elif param_key in [
                    "modifications_offsets",
                    "modifications_y_ion_offsets",
                ]:
                    formatted_masses = self.format_masses(
                        param_value["translated_value"],
                    )
                    print(f"{translated_key:30} = {formatted_masses}", file=fh)
                elif param_key == "score_ion_list":
                    formatted_ion_series = self.format_ion_series(
                        param_value["translated_value"],
                    )
                    print(f"{translated_key:30} = {formatted_ion_series}", file=fh)
                elif param_key == "remove_precursor_range":
                    min_mz, max_mz = param_value["translated_value"]
                    print(f"{translated_key:30} = {min_mz}, {max_mz}", file=fh)
                elif param_key == "delta_mass_exclude_range":
                    min_mz, max_mz = param_value["translated_value"]
                    print(f"{translated_key:30} = ({min_mz}, {max_mz})", file=fh)
                elif param_key == "cpus":
                    if param_value["translated_value"] == "max - 1":
                        import multiprocessing

                        value = multiprocessing.cpu_count() - 1
                    else:
                        value = param_value["translated_value"]
                    print(
                        f"{translated_key:30} = {value}",
                        file=fh,
                    )
                else:
                    print(
                        f"{translated_key:30} = {param_value['translated_value']}",
                        file=fh,
                    )
            # Define precursor_charge param, which would be used if
            # use_spectrum_charge will be set to "no"
            min_charge = utrace.urun_dict.translations["all_params"][
                "precursor_min_charge"
            ]["translated_value"]
            max_charge = utrace.urun_dict.translations["all_params"][
                "precursor_max_charge"
            ]["translated_value"]
            print(f"{'precursor_charge':30} = {min_charge} {max_charge}", file=fh)
            for key, value in formatted_mods.items():
                print(f"{key:30} = {value}", file=fh)
            fasta_file = utrace.input_files.get_path_objects_by_uftype(
                urgap.uftypes.proteomics.FASTA,
            )[0]

            print(
                "database_name = {db}".format(db=f"{fasta_file}"),
                file=fh,
            )
            print("output_file_extension = tsv", file=fh)
            print("output_format = tsv", file=fh)
            # Allow for selenocysteine searches
            print("add_U_user_amino_acid = 0.000000", file=fh)
        self.tmp_files.append(msfragger_param_path)
        return msfragger_param_path

    def format_mods(self, mapped_mods: dict) -> dict:
        """Format  mods into proper style, which is printed into the params template and used by the msfragger search.

        Args:
            mapped_mods: Dict of opt and fix mods to be formatted.

        Returns:
           Dict with formatted mods in msfragger format.
        """
        mass_to_mod_aa = ddict(list)
        formatted_mods = {}
        for mod_dict in mapped_mods["opt"]:
            """
            {'_id': 0,
              'aa': '*',
              'composition': {'C': 2, 'H': 2, 'O': 1},
              'id': '1',
              'mass': 42.010565,
              'name': 'Acetyl',
              'org': '*,opt,Prot-N-term,Acetyl',
              'pos': 'Prot-N-term',
              'unimod': True},
            """
            aa_to_append = mod_dict["aa"]
            pos_modifier = None
            if mod_dict["position"] == "Prot-N-term":
                pos_modifier = "["
            elif mod_dict["position"] == "Prot-C-term":
                pos_modifier = "]"
            elif mod_dict["position"] == "N-term":
                pos_modifier = "n"
            elif mod_dict["position"] == "C-term":
                pos_modifier = "c"
            elif mod_dict["position"] == "any":
                pass
            else:
                raise ValueError(
                    """
                Unknown positional argument for given modification:
                {}
                MSFragger cannot deal with this, please use one of the follwing:
                any, Prot-N-term, Prot-C-term, N-term, C-term
                """.format(mod_dict["org"]),
                )
            if pos_modifier is not None:
                aa_to_append = f"{pos_modifier}{aa_to_append}"
            mass_to_mod_aa[mod_dict["mass"]].append(aa_to_append)
        for pos, (mass, aa_list) in enumerate(mass_to_mod_aa.items()):
            formatted_mods[f"variable_mod_0{pos + 1}"] = "{} {}".format(
                mass,
                "".join(aa_list),
            )
        for mod_dict in mapped_mods["fix"]:
            """
            add_C_cysteine = 57.021464             # added to C - avg. 103.1429, mono. 103.00918
            """
            if mod_dict["position"] == "Prot-N-term":
                mod_key = "add_Nterm_protein"
            elif mod_dict["position"] == "Prot-C-term":
                mod_key = "add_Cterm_protein"
            elif mod_dict["position"] == "N-term":
                mod_key = "add_Nterm_peptide"
            elif mod_dict["position"] == "C-term":
                mod_key = "add_Cterm_peptide"
            else:
                mod_key = "add_{}_{}".format(
                    mod_dict["aa"],
                    chemical_composition_kb.aa_names[mod_dict["aa"]],
                )
            formatted_mods[mod_key] = mod_dict["mass"]
        return formatted_mods

    def format_diagnostic_fragments(self, param_value: dict):
        """Format the user provided diagnostic fragments into msfragger suitable format.

        Args:
            param_value: Dict of lists containing information about molecules to be used as diagnostic fragments.

        Returns:
            String of formatted masses separated by a '/'.
        """
        cc = ChemicalComposition()
        masses = []
        # BUG: if 0 in param_value['masses'], the resulting mz calculated below will be
        # BUG:  the mass of a PROTON, is it correct or should it stay zero?
        for m in param_value["masses"]:
            masses.append(m)
        for m in param_value["glycans"]:
            cc.clear()
            cc.add_glycan(m)
            masses.append(cc._mass())
        for m in param_value["chemical_formulas"]:
            cc.clear()
            cc.add_chemical_formula(m)
            masses.append(cc._mass())
        for m in param_value["unimods"]:
            unimod_mass = self.umama.name2mass(m)
            masses.append(unimod_mass)
        mzs = []
        for mass in masses:
            mzs.append(str(calculate_mz(mass, 1)))
        return "/".join(mzs)

    def format_masses(self, param_value: dict) -> str:
        """Format the user provided masses into msfragger suitable format.

        Args:
            param_value: Dict of lists containing information about molecules to be used as masses.

        Returns:
            String of formatted masses separated by a '/'.
        """
        cc = ChemicalComposition()
        masses = []
        for m in param_value["masses"]:
            masses.append(str(m))
        for m in param_value["glycans"]:
            cc.clear()
            cc.add_glycan(m)
            mass = cc._mass()
            masses.append(str(mass))
            tm = round(mass * 1e5)
            if tm not in self.mass_glycan_lookup:
                self.mass_glycan_lookup[tm] = set()
            self.mass_glycan_lookup[tm].add(m)
        for m in param_value["chemical_formulas"]:
            cc.clear()
            cc.add_chemical_formula(m)
            mass = cc._mass()
            masses.append(str(mass))
            tm = round(mass * 1e5)
            if tm not in self.mass_shift_lookup:
                self.mass_shift_lookup[tm] = set()
            self.mass_shift_lookup[tm].add(m)
        for m in param_value["unimods"]:
            unimod_mass = self.umama.name2mass(m)
            masses.append(str(unimod_mass))
            tm = round(mass * 1e5)
            if tm not in self.mass_shift_lookup:
                self.mass_shift_lookup[tm] = set()
            self.mass_shift_lookup[tm].add(m)
        return "/".join(masses)

    def format_ion_series(self, param_value: list) -> str:
        """Format the user provided ion list into msfragger suitable format.

        Args:
            param_value: List of scoring ions to be formatted.

        Returns:
            String of scoring ions separated by a ','.
        """
        ion_list = []
        for ion in param_value:
            if ion not in [
                "a",
                "b",
                "c",
                "y~",
                "x",
                "y",
                "z",
                "b~",
                "y-18",
                "b-18",
                "Y",
            ]:
                msg = f"MSFragger does not allow the following ion: {ion} This ion will be skipped, i.e. not included in the search."
                logging.warning(msg)
                continue
            ion_list.append(ion)
        return ",".join(ion_list)

    # def execute(self, utrace: urgap.UTrace,) -> urgap.UTrace:
    #     """
    #     Execute routine for msfragger_3 wrapper.

    #     Builds and executes the command_list.

    #     Args:
    #         utrace: Combination of urun_dict, ufile_list and unode.meta.

    #     Returns:
    #         None
    #     """
    #     mgf_index = utrace.input_files.get_indices_by_uftype(
    #         urgap.uftypes.proteomics.converter.PYMZML_MGF
    #     )[0]
    #     command_list = [
    #         "java",
    #         f"-Xmx"
    #         f"{utrace.urun_dict.translations['all_params']['-xmx']['translated_value']}",
    #         "-jar",
    #         str(self.exe_path),
    #         str(self.param_file_path),
    #         str(utrace.input_files[mgf_index].path),
    #     ]
    #     logging.debug(" ".join(command_list))
    #     process = subprocess.Popen(command_list)
    #     process.communicate()

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for msfragger_3 wrapper.

        During preflight,
            - parameters are formatted
            - mods are mapped and formatted
            - param file is written

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
        self.param_file_path = self.write_param_file(utrace)

        mgf_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.converter.PYMZML_MGF,
        )[0]
        utrace.urun_dict.command_list = [
            "java",
            f"-Xmx"
            f"{utrace.urun_dict.translations['all_params']['-xmx']['translated_value']}",
            "-jar",
            str(self.exe_path),
            str(self.param_file_path),
            str(mgf_file),
        ]
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for msfragger_3 wrapper.

        During postflight the msfragger native .tsv output file is converted into the
        pre-defined urgap output file, which is of csv format.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        full_path = utrace.input_files[0].path
        msfragger_tsv = full_path.parent / full_path.with_suffix(".tsv").name
        self.tmp_files.append(msfragger_tsv)

        with (
            open(msfragger_tsv) as fin,
            open(utrace.output_files[0].path, "w") as fout,
        ):
            fout.writelines(fin)
        return utrace


def calculate_mz(mass, charge):
    """Calculate m/z function.

    Args:
        mass (float): mass for calculating m/z
        charge (int): charge for calculating m/z

    Returns:
        calc_mz (float): calculated m/z
    """
    mass = float(mass)
    charge = int(charge)
    calc_mz = (mass + (charge * chemical_composition_kb.PROTON)) / charge
    return calc_mz
