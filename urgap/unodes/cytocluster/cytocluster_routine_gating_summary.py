"""Urgap CytoClusterRoutineGatingSummary wrapper."""

import os

from pathlib import Path

import urgap


class CytoClusterRoutineGatingSummary(urgap.unode.UNodeBase):
    """Urgap wrapper for the routine gating summary script of the CytoCluster Pipeline."""

    _path = "Cytocluster/scripts/4_summary_routine_gating.R"

    META_INFO = {
        "name": "CytoClusterRoutineGatingSummary",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {
                "version": "1.3.0",
                "exe_path": _path,
            },
            {
                "version": "1.4.1",
                "exe_path": _path,
            },
            {
                "version": "1.4.2",
                "exe_path": _path,
            },
        ],
        "input_uftypes": {
            urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_STATS_TSV: {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.flow_cytometry.qc.summary.ROUTINE_GATING_STATS_JPG: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.summary.ROUTINE_GATING_STATS_XLSX: {
                "min": 1,
                "max": 1,
            },
        },
        "engine": None,
        "engine_type": ("flow_cytometry", "qc"),
        "citation": """
        Stefano Pirro
        """,
    }

    def __init__(self) -> None:
        """Initialize cytocluster_routine_gating_summary class."""
        super().__init__()

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
        utrace.urun_dict.command_list.extend(["Rscript", str(self.exe_path)])
        for parameter_key in utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ]:
            if parameter_key in ["--inputDir", "--outDir"]:
                utrace.urun_dict.command_list.extend(
                    [parameter_key, str(utrace.output_files[0].path.parent)],
                )

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for cytocluster_routine_gating_summary wrapper.

        During preflight,
            - parameters are formatted
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict["old_dir"] = Path.getcwd()
        os.chdir(self.exe_path.parent.parent)
        utrace = self.create_command_list(utrace=utrace)

        for i, input_file in enumerate(utrace.input_files):
            target_path = utrace.output_files[0].path.parent / f"{i}_gating_stats.tsv"
            target_path.symlink_to(input_file.path)
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for cytocluster_routine_gating_summary wrapper.

            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        os.chdir(utrace.urun_dict["old_dir"])
        output_types = utrace.output_files.get_path_object_groups_by_uftypes()
        Path.rename(
            src=utrace.output_files[0].path.parent / "routine_gating_stats_report.xlsx",
            dst=output_types[
                urgap.uftypes.flow_cytometry.qc.summary.ROUTINE_GATING_STATS_XLSX
            ][0],
        )
        Path.rename(
            src=utrace.output_files[0].path.parent / "routine_gating_stats.jpg",
            dst=output_types[
                urgap.uftypes.flow_cytometry.qc.summary.ROUTINE_GATING_STATS_JPG
            ][0],
        )
        return utrace
