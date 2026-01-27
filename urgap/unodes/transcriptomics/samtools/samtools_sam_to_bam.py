"""Urgap samtools SAM to BAM file wrapper."""

import urgap


class SamtoolsSamToBam(urgap.unode.UNodeBase):
    """Urgap wrapper for samtools SAM to BAM / view.

    https://github.com/samtools/samtools/releases
    """

    META_INFO = {
        "name": "SamtoolsSamToBam",
        "versions": [
            {
                "version": "1.22.1",
                "exe_path": "$samtools",
            },
        ],
        "parameters_not_triggering_rerun": [],
        "engine": None,
        "engine_type": ("converter", "ngs"),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "input_uftypes": {
            urgap.uftypes.transcriptomics.reads.SAM: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.reads.BAM: {"min": 1, "max": 1},
        },
        "citation": """
        Li, H., Handsaker, B., Wysoker, A., Fennell, T., Ruan, J., Homer, N., Marth, G., Abecasis, G., & Durbin, R. (2009).
        The Sequence Alignment/Map format and SAMtools. In Bioinformatics (Vol. 25, Issue 16, pp. 2078-2079).
        Oxford University Press (OUP). https://doi.org/10.1093/bioinformatics/btp352
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize SamtoolsSamToBam class."""
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
            str(self.exe_path),
            "view",
            "-Sb",
            str(utrace.input_files[0].path),
            "-o",
            str(utrace.output_files[0].path),
        ]
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for SamtoolsSamToBam wrapper.

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
        """Postflight routine for SamtoolsSamToBam wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        return utrace
