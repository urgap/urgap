"""Urgap rp_codon_metrics_1_0_0 wrapper."""

import os

import urgap


class rp_codon_metrics_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the ribosome profiling codon metrics 1.0.0 resource."""

    META_INFO = {
        "name": "rp_codon_metrics_1_0_0",
        "version": "1.0.0",
        "release_date": "06.02.2023",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "api_port": 42910,
        "engine_type": ("qc", "transcriptomics"),
        "platform_independent": True,
        "engine": {
            "platform_independent": {
                "arc_independent": {"exe": "rp_codon_metrics_1_0_0.py"},
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "unimod_mapper",
                    "pyarrow",
                ],
            },
        },
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
        "utranslation_style": "rp_style_1",
        "citation": "Urgap team (2023)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize rp_codon_metrics_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for rp_codon_metrics_1_0_0 wrapper.

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
        for value in utrace.urun_dict.translations["all_params"].values():
            if value["translated_value"] is not None:
                utrace.urun_dict.command_list.append(value["translated_key"])
                utrace.urun_dict.command_list.append(value["translated_value"])

        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for rp_codon_metrics_1_0_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        output_file_groups = utrace.output_files.get_path_object_groups_by_uftypes()
        analysis_feather = output_file_groups[
            urgap.uftypes.transcriptomics.RIBOSOME_PROFILING_FEATHER
        ][0]
        os.rename(
            src=analysis_feather.parent / "analysis.feather",
            dst=analysis_feather,
        )
        html_file = output_file_groups[
            urgap.uftypes.transcriptomics.CODON_METRICS_PLOT_HTML
        ][0]
        os.rename(src=html_file.parent / "plots.html", dst=html_file)
        return utrace
