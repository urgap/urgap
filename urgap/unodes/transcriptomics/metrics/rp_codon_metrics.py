"""Urgap RpCodonMetrics wrapper."""

import urgap


class RpCodonMetrics(urgap.unode.UNodeBase):
    """Urgap wrapper for the ribosome profiling codon metrics resource.

    Note:
        Requires python package 'unimod_mapper' and 'pyarrow' installed in the environment.
    """

    META_INFO = {
        "name": "RpCodonMetrics",
        "versions": [
            {
                "version": "1.0.0",
                "exe_path": "RpCodonMetrics/1_0_0/rp_codon_metrics.py",
            },
        ],
        "parameters_not_triggering_rerun": [],
        "engine": None,
        "engine_type": ("qc", "transcriptomics"),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "input_uftypes": {
            urgap.uftypes.transcriptomics.reads.SAM: {"min": 1, "max": -1},
            urgap.uftypes.transcriptomics.GTF: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.transcriptomics.FASTA: {"min": 0, "max": 1},
            urgap.uftypes.exp_design.output.NGS_METADATA_CSV: {"min": 0, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.CODON_METRICS_PLOT_HTML: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.transcriptomics.RIBOSOME_PROFILING_FEATHER: {
                "min": 1,
                "max": 1,
            },
        },
        "citation": "Urgap team (2023)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize RpCodonMetrics class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for RpCodonMetrics wrapper.

        During preflight,
            - parameters are formatted
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        gtf = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.transcriptomics.GTF,
        )[0]
        sams = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.transcriptomics.reads.SAM,
        )
        sams = ",".join([str(sam) for sam in sams])
        fasta = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.transcriptomics.FASTA,
        )
        metadata = utrace.input_files.get_path_objects_by_uftype(
            uftype=urgap.uftypes.exp_design.output.NGS_METADATA_CSV,
        )
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-g",
            str(gtf),
            "-s",
            sams,
            "-o",
            str(utrace.output_files[0].path.parent),
        ]
        if len(fasta) > 0:
            utrace.urun_dict.command_list.append("-f")
            utrace.urun_dict.command_list.append(fasta[0])
        if len(metadata) > 0:
            utrace.urun_dict.command_list.append("-m")
            utrace.urun_dict.command_list.append(metadata[0])
        for k, v in utrace.urun_dict.items():
            utrace.urun_dict.command_list.extend([k, v])
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for RpCodonMetrics wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        output_file_groups = utrace.output_files.get_path_object_groups_by_uftypes()
        analysis_feather = output_file_groups[
            urgap.uftypes.transcriptomics.RIBOSOME_PROFILING_FEATHER
        ][0]
        (analysis_feather.parent / "analysis.feather").rename(
            analysis_feather,
        )
        html_file = output_file_groups[
            urgap.uftypes.transcriptomics.CODON_METRICS_PLOT_HTML
        ][0]
        (html_file.parent / "plots.html").rename(html_file)
        return utrace