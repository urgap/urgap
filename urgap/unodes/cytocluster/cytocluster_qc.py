"""Urgap CytoClusterQC wrapper."""

import logging
import tempfile

from pathlib import Path

import urgap

logger = logging.getLogger(__name__)


class CytoClusterQC(urgap.unode.UNodeBase):
    """Urgap wrapper for the QC script of the CytoCluster Pipeline."""

    _path = "Cytocluster/scripts/1_QC.R"

    META_INFO = {
        "name": "CytoClusterQC",
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
            urgap.uftypes.flow_cytometry.FCS: {"min": 1, "max": 1},
            urgap.uftypes.flow_cytometry.CALIBRATION_FCS: {"min": 0, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.flow_cytometry.FCS: {"min": 1, "max": 1},
            urgap.uftypes.flow_cytometry.qc.reports.FLOWAI_QCMINI_TXT: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.reports.FLOWAI_REPORT_HTML: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.reports.PEACOQC_REPORT_TXT: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.reports.PEACOQC_REPORT_PNG: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.reports.FLOWCUT_REPORT_TXT: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.reports.FLOWCUT_REPORT_PNG: {
                "min": 0,
                "max": 2,
            },
        },
        "additional_data": {
            "internal_resource_versions": {
                "flowAI": "1.30.0",
                "flowCut": "1.10.0",
                "peacoQC": "1.10.0",
            },
        },
        "engine": None,
        "engine_type": ("flow_cytometry", "qc"),
        "citation": """
        Monaco, G., Chen, H., Poidinger, M., Chen, J., de Magalhães, J. P., & Larbi, A. (2016).
            flowAI: automatic and interactive anomaly discerning tools for flow cytometry data.
            In Bioinformatics (Vol. 32, Issue 16, pp. 2473-2480). Oxford University Press (OUP). https://doi.org/10.1093/bioinformatics/btw191
        Emmaneel, A., Quintelier, K., Sichien, D., Rybakowska, P., Marañón, C., Alarcón-Riquelme, M. E., Van Isterdael, G., Van Gassen, S., & Saeys, Y. (2021).
            PeacoQC: Peak-based selection of high quality cytometry data.
            In Cytometry Part A (Vol. 101, Issue 4, pp. 325-338). Wiley. https://doi.org/10.1002/cyto.a.24501
        """,
    }

    def __init__(self) -> None:
        """Initialize CytoClusterQC class."""
        super().__init__()
        self.tmp_output_dir = None

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
        calibration_files = ""
        for file in utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.flow_cytometry.CALIBRATION_FCS,
        ):
            calibration_files += str(file) + ","
        calibration_files = calibration_files.rstrip(",")
        utrace.urun_dict.command_list.extend(["Rscript", str(self.exe_path)])

        for parameter_key, parameter_value in utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ].items():
            if parameter_key == "--fcs":
                utrace.urun_dict.command_list.extend(
                    [parameter_key, str(utrace.input_files[0].path)],
                )
            elif parameter_key == "--outDir":
                utrace.urun_dict.command_list.extend(
                    [parameter_key, str(self.tmp_output_dir)],
                )
            elif len(calibration_files) > 0 and parameter_key == "--compensationFiles":
                utrace.urun_dict.command_list.extend(
                    [parameter_key, ",".join(calibration_files)],
                )
            elif parameter_key is None:
                if len(parameter_value) != 0:
                    utrace.urun_dict.command_list.append(parameter_value)
            elif parameter_key == "--qcMethod":
                utrace.urun_dict.command_list.append(parameter_key)
                for method in parameter_value:
                    utrace.urun_dict.command_list.append(method)
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for CytoClusterQC wrapper.

        During preflight,
            - parameters are formatted
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.tmp_output_dir = Path(
            tempfile.mkdtemp(dir=utrace.output_files[0].path.parent),
        )
        return self.create_command_list(utrace=utrace)

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for CytoClusterQC wrapper.

            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        if None in utrace.output_files:
            logger.warning("No output files generated. Not running postflight.")
            return utrace

        stem_name = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.flow_cytometry.FCS,
        )[0].stem

        out_dir = self.tmp_output_dir / stem_name

        annotated_fcs_file = out_dir / (stem_name + "_clinical.fcs")
        annotated_fcs_file.rename(
            utrace.output_files.get_path_objects_by_uftype(
                urgap.uftypes.flow_cytometry.FCS,
            )[0],
        )

        flow_ai_qcmini_file = out_dir / "flowAI" / "QCmini.txt"
        utrace = self._map_output_files(
            utrace=utrace,
            files=[flow_ai_qcmini_file],
            uftype=urgap.uftypes.flow_cytometry.qc.reports.FLOWAI_QCMINI_TXT,
        )
        flow_ai_html_file = out_dir / "flowAI" / (stem_name + "TRUE.html")
        if flow_ai_html_file.exists():
            utrace = self._rename_and_extend_safely(
                utrace=utrace,
                files=[flow_ai_html_file],
                uftype=urgap.uftypes.flow_cytometry.qc.reports.FLOWAI_REPORT_HTML,
            )

        peacoqc_txt_file = out_dir / "peacoQC" / stem_name / "PeacoQC_report.txt"
        utrace = self._map_output_files(
            utrace=utrace,
            files=[peacoqc_txt_file],
            uftype=urgap.uftypes.flow_cytometry.qc.reports.PEACOQC_REPORT_TXT,
        )
        peacoqc_png_file = (
            out_dir
            / "peacoQC"
            / stem_name
            / "PeacoQC_plots"
            / ("PeacoQC_" + stem_name + ".png")
        )
        if peacoqc_png_file.exists():
            utrace = self._rename_and_extend_safely(
                utrace=utrace,
                files=[peacoqc_png_file],
                uftype=urgap.uftypes.flow_cytometry.qc.reports.PEACOQC_REPORT_PNG,
            )

        flowcut_txt_file = out_dir / "flowCut" / (stem_name + "_qc_report.txt")
        utrace = self._map_output_files(
            utrace=utrace,
            files=[flowcut_txt_file],
            uftype=urgap.uftypes.flow_cytometry.qc.reports.FLOWCUT_REPORT_TXT,
        )
        flowcut_png_folder = out_dir / "flowCut"
        flowcut_png_files = [
            f for f in flowcut_png_folder.iterdir() if f.suffix == ".png"
        ]
        if len(flowcut_png_files) > 0:
            utrace = self._rename_and_extend_safely(
                utrace=utrace,
                files=flowcut_png_files,
                uftype=urgap.uftypes.flow_cytometry.qc.reports.FLOWCUT_REPORT_PNG,
            )
        return utrace

    def _map_output_files(
        self,
        utrace: urgap.UTrace,
        files: list[Path],
        uftype: str,
    ) -> urgap.UTrace:
        """Extend output file list if any file exists and rename it appropriately.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
            files: Files to copy.
            uftype: Urgap uftype.
        """
        for i, file in enumerate(files):
            dst = utrace.output_files.get_path_objects_by_uftype(uftype)[i]
            file.rename(target=dst)
        return utrace

    def _rename_and_extend_safely(
        self,
        utrace: urgap.UTrace,
        files: list,
        uftype: str,
    ) -> urgap.UTrace:
        """Extend output file list if any file exists and rename it appropriately.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
            files: List of paths to source files in priority order from highest to lowest.
            uftype: Urgap uftype.
        """
        for source_file in files:
            utrace.extend_output_files_by_uftype(uftype)
            source_file.rename(target=utrace.output_files[-1].path)
        return utrace
