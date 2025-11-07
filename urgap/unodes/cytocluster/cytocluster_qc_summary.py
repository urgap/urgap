"""Urgap CytoClusterQCSummary wrapper."""

import os
import shutil

from pathlib import Path

import urgap


class CytoClusterQCSummary(urgap.unode.UNodeBase):
    """Urgap wrapper for the QC summary script of the CytoCluster Pipeline."""

    _path = "Cytocluster/scripts/2_summary_QC.R"

    META_INFO = {
        "name": "CytoClusterQCSummary",
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
            {
                "version": "1.4.3",
                "exe_path": _path,
            },
            {
                "version": "1.4.4",
                "exe_path": _path,
            },
            {
                "version": "1.4.6",
                "exe_path": _path,
            },
            {
                "version": "1.4.7",
                "exe_path": _path,
            },
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.flow_cytometry.qc.reports.FLOWAI_QCMINI_TXT: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.flow_cytometry.qc.reports.PEACOQC_REPORT_TXT: {
                "min": 1,
                "max": -1,
            },
            urgap.uftypes.flow_cytometry.qc.reports.FLOWCUT_REPORT_TXT: {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.flow_cytometry.qc.summary.FLOWAI_QCSTATS_XLSX: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.summary.FLOWAI_QCSTATS_JPG: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.summary.PEACOQC_REPORT_TXT: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.summary.PEACOQC_REPORT_PNG: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.summary.FLOWCUT_QCSTATS_XLSX: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.summary.FLOWCUT_QCSTATS_JPG: {
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
        """Initialize cytocluster_qc_summary class."""
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
        """Preflight routine for cytocluster_qc_summary wrapper.

        During preflight,
            - parameters are formatted
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict["old_dir"] = Path.cwd()
        os.chdir(self.exe_path.parent.parent)
        utrace = self.create_command_list(utrace=utrace)

        for i, input_file in enumerate(utrace.input_files):
            if (
                input_file.uftype
                == urgap.uftypes.flow_cytometry.qc.reports.FLOWAI_QCMINI_TXT
            ):
                shutil.copy(
                    src=input_file.path,
                    dst=f"{utrace.output_files[0].path.parent}/{i}_QCmini.txt",
                )
            elif (
                input_file.uftype
                == urgap.uftypes.flow_cytometry.qc.reports.PEACOQC_REPORT_TXT
            ):
                Path(
                    f"{utrace.output_files[0].path.parent}/peacoQC",
                ).mkdir(parents=True, exist_ok=True)
                shutil.copy(
                    src=input_file.path,
                    dst=f"{utrace.output_files[0].path.parent}/peacoQC/{i}_PeacoQC_report.txt",
                )
            elif (
                input_file.uftype
                == urgap.uftypes.flow_cytometry.qc.reports.FLOWCUT_REPORT_TXT
            ):
                shutil.copy(
                    src=input_file.path,
                    dst=f"{utrace.output_files[0].path.parent}/{i}_qc_report.txt",
                )
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for cytocluster_qc_summary wrapper.

            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        os.chdir(utrace.urun_dict["old_dir"])
        qc_methods = utrace.input_files.get_path_object_groups_by_uftypes()
        output_types = utrace.output_files.get_path_object_groups_by_uftypes()
        if urgap.uftypes.flow_cytometry.qc.reports.FLOWAI_QCMINI_TXT in qc_methods:
            (
                utrace.output_files[0].path.parent
                / "FlowAI_quality_control_report.xlsx"
            ).rename(
                output_types[
                    urgap.uftypes.flow_cytometry.qc.summary.FLOWAI_QCSTATS_XLSX
                ][0],
            )
            (utrace.output_files[0].path.parent / "flowAI_QC_stats.jpg").rename(
                output_types[
                    urgap.uftypes.flow_cytometry.qc.summary.FLOWAI_QCSTATS_JPG
                ][0],
            )
        if urgap.uftypes.flow_cytometry.qc.reports.PEACOQC_REPORT_TXT in qc_methods:
            (utrace.output_files[0].path.parent / "PeacoQC_report.txt").rename(
                output_types[
                    urgap.uftypes.flow_cytometry.qc.summary.PEACOQC_REPORT_TXT
                ][0],
            )
            (utrace.output_files[0].path.parent / "PeacoQC_report.png").rename(
                output_types[
                    urgap.uftypes.flow_cytometry.qc.summary.PEACOQC_REPORT_PNG
                ][0],
            )
        if urgap.uftypes.flow_cytometry.qc.reports.FLOWCUT_REPORT_TXT in qc_methods:
            (
                utrace.output_files[0].path.parent
                / "FlowCut_quality_control_report.xlsx"
            ).rename(
                output_types[
                    urgap.uftypes.flow_cytometry.qc.summary.FLOWCUT_QCSTATS_XLSX
                ][0],
            )
            (utrace.output_files[0].path.parent / "flowCut_QC_stats.jpg").rename(
                output_types[
                    urgap.uftypes.flow_cytometry.qc.summary.FLOWCUT_QCSTATS_JPG
                ][0],
            )
        return utrace
