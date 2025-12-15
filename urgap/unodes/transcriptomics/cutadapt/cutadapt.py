"""Urgap CutAdapt wrapper."""

import multiprocessing as mp

import urgap


class CutAdapt(urgap.unode.UNodeBase):
    """Urgap wrapper for the cutadapt short read aligner.

    https://pypi.org/project/cutadapt/#description
    """

    META_INFO = {
        "name": "CutAdapt",
        "versions": [
            {
                "version": "5.2",
                "exe_path": "$cutadapt",
            },
        ],
        "parameters_not_triggering_rerun": ["--cores"],
        "engine": None,
        "engine_type": ("aligner", "ngs"),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
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
        """Initialize CutAdapt class."""
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
        if "--cores" not in utrace.urun_dict:
            utrace.urun_dict.command_list.extend(["--cores", str(mp.cpu_count() - 1)])
        for k, v in utrace.urun_dict.items():
            utrace.urun_dict.command_list.extend([k, v])
        utrace.urun_dict.command_list.append("-o")
        utrace.urun_dict.command_list.append(str(utrace.output_files[0].path))
        utrace.urun_dict.command_list.append(str(utrace.input_files[0].path))

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for CutAdapt wrapper.

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
        """Postflight routine for CutAdapt wrapper.

            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        return utrace