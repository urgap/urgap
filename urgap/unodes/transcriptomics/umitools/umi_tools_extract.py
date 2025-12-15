"""Urgap UmiToolsExtract wrapper."""

import urgap


class UmiToolsExtract(urgap.unode.UNodeBase):
    """Urgap wrapper for UmiToolsExtract.

    https://pypi.org/project/umi-tools/
    """

    META_INFO = {
        "name": "UmiToolsExtract",
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
            urgap.uftypes.transcriptomics.reads.FASTQ_GZ: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.reads.FASTQ_GZ: {"min": 1, "max": 1},
        },
        "citation": """
        Smith, T., Heger, A., & Sudbery, I. (2017).
        UMI-tools: modeling sequencing errors in Unique Molecular Identifiers to improve quantification accuracy.
        In Genome Research (Vol. 27, Issue 3, pp. 491-499). Cold Spring Harbor Laboratory.
        https://doi.org/10.1101/gr.209601.116
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize UmiToolsExtract class."""
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
            "extract",
        ]
        utrace.urun_dict.command_list += ["-I", str(utrace.input_files[0].path)]
        for k, v in utrace.urun_dict.items():
            utrace.urun_dict.command_list.extend([k, v])
        utrace.urun_dict.command_list += ["-S", str(utrace.output_files[0].path)]
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for UmiToolsExtract wrapper.

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
        """Postflight routine for UmiToolsExtract wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        return utrace