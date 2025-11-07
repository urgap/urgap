"""Urgap UMIToolsExtract_1_4_4 wrapper."""

import os

import urgap


class UMIToolsExtract_1_4_4(urgap.unode.UNodeBase):
    """Urgap wrapper for UMI-tools 1.1.4."""

    META_INFO = {
        "name": "umi_tools_dedup_1_1_4",
        "version": "1.1.4",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "02.03.2023",
        "api_port": 42917,
        "engine_type": ("ngs",),
        "platform_independent": True,
        "utranslation_style": "umi_tools_dedup_style_1",
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "umi_tools_dedup_1_1_4.py",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ("umi_tools",),
            },
        },
        "input_uftypes": {
            urgap.uftypes.transcriptomics.reads.BAM: {"min": 1, "max": 1},
            urgap.uftypes.transcriptomics.BAM_INDEX: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.reads.BAM: {"min": 1, "max": 1},
        },
        "citation": """
        Smith, T., Heger, A., & Sudbery, I. (2017).
        UMI-tools: modeling sequencing errors in Unique Molecular Identifiers to improve quantification accuracy.
        In Genome Research (Vol. 27, Issue 3, pp. 491-499). Cold Spring Harbor Laboratory.
        https://doi.org/10.1101/gr.209601.116
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize UMIToolsExtract_1_4_4 class."""
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
            "umi_tools",
            "dedup",
        ]
        utrace.urun_dict.command_list += [
            "-I",
            str(utrace.input_files[0].path),
        ]
        for value in utrace.urun_dict.translations["all_params"].values():
            utrace.urun_dict.command_list.append(value["translated_key"])
            utrace.urun_dict.command_list.append(str(value["translated_value"]))
        utrace.urun_dict.command_list += [
            "-S",
            str(utrace.output_files[0].path),
        ]
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for UMIToolsExtract_1_4_4 wrapper.

        During preflight,
            - parameters are formatted
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        bam = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.reads.BAM,
        )[0]
        bam_index = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.BAM_INDEX,
        )[0]
        os.symlink(src=bam_index, dst=bam.with_suffix(".bam.bai"))
        return self.create_command_list(utrace=utrace)

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for UMIToolsExtract_1_4_4 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        return utrace
