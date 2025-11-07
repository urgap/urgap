"""Urgap mascot_2_6_2 wrapper."""

import copy
import logging
import subprocess

from datetime import datetime

try:
    from unimod_mapper import UnimodMapper
except:
    pass

import urgap


class mascot_2_6_2(urgap.unode.UNodeBase):
    """Urgap wrapper for the mascot_2_6_2 search engine.

    Mascot is a MS/MS sequence database search tool for identification,
    characterisation and quantitation of proteins using mass spectrometry data.
    See publication provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "mascot_2_6_2",
        "version": "2.6.2",
        "release_date": "28.05.2021",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "api_port": 42708,
        "engine_type": ("db_search", "proteomics"),
        "platform_independent": True,
        "utranslation_style": "mascot_style_1",
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "nph-mascot.exe",
                    "url": "",
                    "zip_md5": "",
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
            urgap.uftypes.proteomics.dbsearch.MASCOT_DAT: {"min": 1, "max": 1},
        },
        "citation": """
        Perkins, D. N., Pappin, D. J. C., Creasy, D. M., & Cottrell, J. S. (1999). Probability-based protein identification by searching sequence databases using mass spectrometry data.
        In Electrophoresis (Vol. 20, Issue 18, pp. 3551-3567). Wiley. https://doi.org/10.1002/(sici)1522-2683(19991201)20:18<3551::aid-elps3551>3.0.co;2-2
        """,
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize mascot_2_6_2 class."""
        super().__init__(*args, **kwargs)

    def write_mimefile(
        self,
        utrace: urgap.UTrace,
    ):
        """Write mime file used by the mascot search engine.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta - to be written out.
        """
        boundary = "gc0p4Jq49782jU35Frq980"
        ftcparams = utrace.urun_dict.translations["formatted_all_params"]
        self.mimepath = str(self.input_file.with_suffix(".asc"))
        with open(self.mimepath, "w") as mimefile:
            for _key, dict in ftcparams.items():
                translated_dict_key = dict["translated_key"]
                translated_dict_value = dict["translated_value"]
                if (
                    translated_dict_key
                    in [
                        "TOL_part1",
                        "TOL_part2",
                        "CHARGE_min",
                        "CHARGE_max",
                        ("MODS", "IT_MODS"),
                    ]
                    or translated_dict_value is None
                ):
                    continue
                if len(dict) == 2 or len(dict) == 4 or "was_translated" in dict:
                    mimefile.write(f"--{boundary}\n")
                    mimefile.write(
                        f'Content-Disposition: form-data; name="{translated_dict_key}"\n\n',
                    )
                    mimefile.write(f"{translated_dict_value}\n")
                else:
                    print(
                        "The translated key ",
                        translated_dict_key,
                        " maps on more than one ukey, but no special rules have been "
                        "defined",
                    )
            mimefile.write(f"--{boundary}\n")
            mimefile.write(
                f'Content-Disposition: form-data; name="FILE"; filename="{self.input_file}"\n\n',
            )
            with open(str(self.input_file)) as mgf_in:
                mimefile.writelines(mgf_in)
                mimefile.write("\n\n")
                mimefile.write(f"--{boundary}--\n")

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for mascot_2_6_2 wrapper.

        During preflight,
            - mods and params are formatted
            - the MIME file in .asc format is written
            - analysis folder is created & MIME file copied to the mascot server
                (naming convention is not changed between local and remote!)

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta - to be written out.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.converter.PYMZML_MGF,
        )[0]

        self.fasta_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.FASTA,
        )[0]

        unimod_xml_list = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.MODS_XML,
        )
        self.mod_mapper = UnimodMapper(
            xml_file_list=unimod_xml_list,
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
        utrace.urun_dict.translations["formatted_all_params"].update(self.format_mods())
        self.write_mimefile(utrace=utrace)

        # define params relevant for ssh
        # stored in self to be used for pre-flight, execute & post-flight
        self.analysis_path = f"{utrace.urun_dict.translations['formatted_all_params']['mascot_data_path']['translated_value']}/{datetime.today().strftime('%Y%m%d')}"
        self.user = utrace.urun_dict.translations["formatted_all_params"]["login_name"][
            "translated_value"
        ]
        self.host = utrace.urun_dict.translations["formatted_all_params"]["host"][
            "translated_value"
        ]

        # included a check so execution breaks down if username or host was not
        # provided!
        if any(elem is None for elem in [self.user, self.host]):
            raise OSError(
                """
                    You have to provide a login_name and host to login to the
                    mascot server!
                """,
            )  # not sure about logic here ....

        self.execute_command_list(
            command_list=[
                *self.define_login_info(utrace=utrace, command="ssh"),
                f"{self.user}@{self.host}",
                "[",
                " -d",
                self.analysis_path,
                " ]",
                "||",
                "mkdir -m 777",
                self.analysis_path,
            ],
        )

        # Next step copy the mime file to analysis path
        self.execute_command_list(
            command_list=[
                *self.define_login_info(utrace=utrace, command="scp"),
                self.mimepath,
                f"{self.user}@{self.host}:/{self.analysis_path}",
            ],
        )
        return utrace

    def execute(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Execute routine for mascot_2_6_2 wrapper.

        Executes the mascot search on the provided mascot server (params defined
        during preflight).

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta - to be written out.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.execute_command_list(
            command_list=[
                *self.define_login_info(utrace=utrace, command="ssh"),
                f"{self.user}@{self.host}",
                "cd",
                f"{utrace.urun_dict.translations['formatted_all_params']['mascot_exe_path']['translated_value']}",
                ";",
                f"./{self.META_INFO['engine']['platform_independent']['arc_independent']['exe']}",
                "1",
                "-commandlist",
                "-f",
                f"{self.analysis_path}/{utrace.output_files[0].path.name}",
                "<",
                f"{self.analysis_path}/{self.mimepath.split('/')[-1]}",
            ],
        )
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for mascot_2_6_2 wrapper.

        During postflight the .dat file back from the mascot server. Naming convention
        of the .dat file follow the determine_output_filename logic, both on local &
        remote!

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta - to be written out.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.execute_command_list(
            command_list=[
                *self.define_login_info(utrace=utrace, command="scp"),
                f"{self.user}@{self.host}:/"
                f"{self.analysis_path}/"
                f"{utrace.output_files[0].path.name}",
                f"{utrace.output_files[0].path!s}",
            ],
        )
        # should that not be part of the urun_dict?
        return utrace

    def format_params(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Format params into a format expected by the comet search engine.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta - to be written out.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.translations["formatted_all_params"] = copy.deepcopy(
            utrace.urun_dict.translations["all_params"],
        )

        ftcparams = utrace.urun_dict.translations["formatted_all_params"]

        ftcparams["mgf_input_file"]["translated_value"] = str(self.input_file)

        ftcparams["database"]["translated_value"] = self.fasta_file.name

        considered_charges = []
        for charge in range(
            int(ftcparams["precursor_min_charge"]["translated_value"]),
            int(ftcparams["precursor_max_charge"]["translated_value"]) + 1,
        ):
            considered_charges.append(f"{charge}+")
        ftcparams["considered_charges"] = {
            "translated_key": "CHARGE",
            "translated_value": ", ".join(considered_charges),
        }

        precursor_error = (
            float(ftcparams["precursor_mass_tolerance_minus"]["translated_value"])
            + float(ftcparams["precursor_mass_tolerance_plus"]["translated_value"])
        ) / 2.0
        ftcparams["precursor_mass_tolerance"] = {
            "translated_key": "TOL",
            "translated_value": precursor_error,
        }
        logging.info(
            """
            [ WARNING ] precursor_mass_tolerance_plus and precursor_mass_tolerance_minus
            [ WARNING ] need to be combined for pyQms (use of symmetric tolerance window).
            [ WARNING ] The arithmetic mean is used.
            """,
        )

        ftcparams["remove_precursor_range"]["translated_value"] = ",".join(
            str(e) for e in ftcparams["remove_precursor_range"]["translated_value"]
        )
        return utrace

    def format_mods(self) -> dict:
        """Format mods into proper style, which is required by mascot.

        Returns:
            Dict with formatted fixed mods in mascot format.
        """
        formatted_mods = {}
        potential_mods = []
        fixed_mods = []
        for mod in self.mapped_mods["fix"]:
            if mod["aa"] != "*":
                fixed_mods.append("{} ({})".format(mod["name"], mod["aa"]))
            elif mod["aa"] == "*" and "N-Term" in mod["position"]:
                potential_mods.append("{} ({})".format(mod["name"], "N-term"))
            elif mod["aa"] == "*" and "C-Term" in mod["position"]:
                potential_mods.append("{} ({})".format(mod["name"], "C-term"))
            else:
                logging.warning(
                    "No matching site could be determined for {} at position "
                    "{}. Mod will be skipped".format(mod["name"], mod["position"]),
                )
                continue
        for mod in self.mapped_mods["opt"]:
            if mod["aa"] != "*":
                potential_mods.append("{} ({})".format(mod["name"], mod["aa"]))
            elif mod["aa"] == "*" and "N-term" in mod["position"]:
                potential_mods.append("{} ({})".format(mod["name"], "N-term"))
            elif mod["aa"] == "*" and "C-term" in mod["position"]:
                potential_mods.append("{} ({})".format(mod["name"], "C-term"))
            else:
                logging.warning(
                    "No matching site could be determined for {} at position "
                    "{}. Mod will be skipped".format(mod["name"], mod["position"]),
                )
                continue

        formatted_mods["fixed_modifications"] = {
            "translated_key": "MODS",
            "translated_value": ",".join(fixed_mods),
        }
        formatted_mods["potential_modifications"] = {
            "translated_key": "IT_MODS",
            "translated_value": ",".join(potential_mods),
        }
        return formatted_mods

    def execute_command_list(
        self,
        command_list: list | None = None,
    ):
        """Execute any command list provided using subprocess.

        Args:
            command_list: Formatted command_list to be executed.
        """
        # this could be rather a general function as it can be used in any wrapper!

        execute_answer = []
        proc = subprocess.Popen(
            command_list,
            stdout=subprocess.PIPE,
        )
        if proc is not None:
            for line in proc.stdout:
                try:
                    line_decoded = line.strip().decode("utf")
                except:
                    line_decoded = line.strip().decode("unicode_escape")
                logging.info(line_decoded)
                execute_answer.append(line_decoded)

    def define_login_info(
        self,
        utrace: urgap.UTrace,
        command: str | None = None,
    ) -> list:
        """Define the basic login information.

        Information like the command to execute, the identity path and port to use.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
            command: Command to be executed.

        Returns:
            Command_list to be piped to subprocess.
        """
        tcparams = utrace.urun_dict.translations["formatted_all_params"]
        clist = [command]
        if tcparams["identity_file"]["translated_value"] is not None:
            clist.extend(
                (
                    tcparams["identity_file"]["translated_key"],
                    tcparams["identity_file"]["translated_value"],
                ),
            )
            # continue
        if tcparams["port"]["translated_value"] is not None:
            if command == "ssh":
                clist.extend(
                    (
                        tcparams["port"]["translated_key"],
                        tcparams["port"]["translated_value"],
                    ),
                )
            elif command == "scp":
                clist.extend(
                    (
                        tcparams["port"]["translated_key"].upper(),
                        tcparams["port"]["translated_value"],
                    ),
                )

        return clist
