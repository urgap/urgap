"""Urgap DESeq2 wrapper."""

import urgap


class DESeq2(urgap.unode.UNodeBase):
    """Urgap wrapper for the DESeq2.

    Allows to calculate differential expression.
    """

    META_INFO = {
        "name": "DESeq2",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "1.0.0", "exe_path": "DESeq2/1_0_0/deseq2.R"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.transcriptomics.COUNT_TABLE_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.transcriptomics.METADATA_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.DESEQ2_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.plotter.PCA_PDF: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.plotter.MA_PDF: {
                "min": 1,
                "max": 1,
            },
        },
        "engine": None,
        "engine_type": ("io",),
        "citation": "Urgap team (2021)",
        "parameter_examples": """

            -q: Use R logical expression

            For example:
            {
                "-q": "padj < 0.05 & abs(log2FoldChange) > 1"
            }

            -d: Design of the experiment in DESeq2

            For example:
            {
            "-d": "~rep + condition",
            }

            -r: Reference group

            For example:
            {
            "-r": "WT",
            }

            --alpha: FDR threshold used for p-value adjustment and significance labeling

            For example:
            {
            "--alpha": 0.05,
            }

            --plotPCA_intgroup: interaction group for PCA plot

            For example:
            {
            "--plotPCA_intgroup": 'c("condition", "rep")',
            }

            --plotMA_ylim: Y-axis limits for MA plot

            For example:
            {
            "--plotMA_ylim": "c(-5,5)"
            }

            --plotMA_ylab: Y-axis label for MA plot

            For example:
            {
            "--plotMA_ylab": "Log2 fold change"
            }

            --plotMA_xlab: X-axis label for MA plot

            For example:
            {
            "--plotMA_xlab": "Mean expression"
            }

        """,
    }

    def __init__(self) -> None:
        """Initialize DESeq2 class."""
        super().__init__()

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for DESeq2 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = ["Rscript", str(self.exe_path)]
        for file in utrace.input_files:
            utrace.urun_dict.command_list.extend(["-i", str(file.path)])
        for file in utrace.output_files:
            utrace.urun_dict.command_list.extend(["-o", str(file.path)])

        for parameter_key, parameter_value in utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ].items():
            if parameter_value is not None:
                utrace.urun_dict.command_list.extend([parameter_key, parameter_value])
        return utrace
