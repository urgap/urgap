"""Urgap cutadapt_4_1 wrapper."""

import multiprocessing as mp
import re

import urgap


class cutadapt_4_1(urgap.unode.UNodeBase):
    """Urgap wrapper for the cutadapt 4.1 short read aligner."""

    META_INFO = {
        "name": "cutadapt_4_1",
        "version": "1.3.1",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "13.09.2021",
        "api_port": 42906,
        "engine_type": ("aligner", "ngs"),
        "platform_independent": True,
        "utranslation_style": "cutadapt_style_1",
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "cutadapt_4_1.py",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ("cutadapt",),
            },
        },
        "input_uftypes": {
            urgap.uftypes.transcriptomics.reads.FASTQ_GZ: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.reads.FASTQ_GZ: {"min": 1, "max": 1},
            # urgap.uftypes.transcriptomics.CUTADAPT_STATS_JSON: {"min": 1, "max": 1},
        },
        "citation": """
        Martin, M. (2011). Cutadapt removes adapter sequences from high-throughput sequencing reads.
        EMBnet.journal, 17(1), pp. 10-12. doi:https://doi.org/10.14806/ej.17.1.200
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize cutadapt_4_1 class."""
        super().__init__(*args, **kwargs)

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
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
        ]
        for value in utrace.urun_dict.translations["all_params"].values():
            if value["translated_value"] is None:
                continue
            if value["translated_key"] is not None:
                if value["original_key"] == "trim_nt_5_prime":
                    value["translated_key"] = re.sub(
                        r"_<.+>$",
                        "",
                        value["translated_key"],
                    )
                elif value["original_key"] == "trim_nt_3_prime":
                    value["translated_key"] = re.sub(
                        r"_<.+>$",
                        "",
                        value["translated_key"],
                    )
                    value["translated_value"] *= -1
                elif (value["original_key"] == "cpus") and (
                    value["translated_value"] == -1
                ):
                    value["translated_value"] = mp.cpu_count() - 1
                utrace.urun_dict.command_list.append(value["translated_key"])
            if len(str(value["translated_value"])) != 0:
                utrace.urun_dict.command_list.append(str(value["translated_value"]))
        utrace.urun_dict.command_list.append("-o")
        utrace.urun_dict.command_list.append(str(utrace.output_files[0].path))
        utrace.urun_dict.command_list.append(str(utrace.input_files[0].path))

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for cutadapt_4_1 wrapper.

        During preflight,
            - parameters are formatted
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        return self.create_command_list(utrace=utrace)

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for cutadapt_4_1 wrapper.

            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        return utrace
