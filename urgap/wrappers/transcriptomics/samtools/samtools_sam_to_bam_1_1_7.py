"""Urgap samtools SAM to BAM file wrapper."""

import urgap


class SamtoolsSAMtoBAM_1_7_1(urgap.unode.UNodeBase):
    """Urgap wrapper for samtools SAM to BAM / view."""

    META_INFO = {
        "name": "samtools_sam_to_bam_1_7_1",
        "version": "1.7.1",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "21.02.2023",
        "api_port": 42913,
        "engine_type": ("converter", "ngs"),
        "platform_independent": False,
        "utranslation_style": "samtools_sam_to_bam_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "samtools",
                    "uri": None,
                    "urn": "darwin/arm64/samtools_1_7_1.zip",
                    "urn_md5": "7bfb3505dfd3de39ecb82579e725dcc5",
                    "external_url": None,
                    "external_md5": None,
                },
                "x86_64": {
                    "exe": "samtools",
                    "uri": None,
                    "urn": "darwin/x86_64/samtools_1_7_1.zip",
                    "urn_md5": "7bfb3505dfd3de39ecb82579e725dcc5",
                    "external_url": None,
                    "external_md5": None,
                },
            },
            "linux": {
                "arm64": {
                    "exe": "samtools",
                    "uri": None,
                    "urn": "linux/arm64/samtools_1_7_1.zip",
                    "urn_md5": "7c8cba1768b6c6382d0bb20a2b47dade",
                    "external_url": None,
                    "external_md5": None,
                },
                "x86_64": {
                    "exe": "samtools",
                    "uri": None,
                    "urn": "linux/x86_64/samtools_1_7_1.zip",
                    "urn_md5": "7c8cba1768b6c6382d0bb20a2b47dade",
                    "external_url": None,
                    "external_md5": None,
                },
            },
        },
        "exe_path": "samtools_1_7_1/samtools",
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
        """Initialize SamtoolsSAMtoBAM_1_7_1 class."""
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
        """Preflight routine for samtools_sam_to_bam_1_7_1 wrapper.

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
        """Postflight routine for samtools_sam_to_bam_1_7_1 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        return utrace
