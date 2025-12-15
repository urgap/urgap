"""Urgap UmiToolsDedup wrapper."""

import urgap


class UmiToolsDedup(urgap.unode.UNodeBase):
    """Urgap wrapper for UmiToolsDedup.

    https://pypi.org/project/umi-tools/
    """

    META_INFO = {
        "name": "UmiToolsDedup",
        "versions": [
            {
                "version": "1.1.6",
                "exe_path": "$umi_tools",
            },
        ],
        "parameters_not_triggering_rerun": [],
        "engine": None,
        "engine_type": ("ngs",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
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
        """Initialize UmiToolsDedup class."""
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
            self.exe_path,
            "dedup",
        ]
        utrace.urun_dict.command_list += [
            "-I",
            str(utrace.input_files[0].path),
        ]
        for k, v in utrace.urun_dict.items():
            utrace.urun_dict.command_list.extend([k, v])
        utrace.urun_dict.command_list += [
            "-S",
            str(utrace.output_files[0].path),
        ]
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for UmiToolsDedup wrapper.

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
        return self.create_command_list(utrace=utrace)

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for UmiToolsDedup wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        return utrace