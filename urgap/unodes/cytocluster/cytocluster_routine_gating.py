"""Urgap CytoClusterRoutineGating wrapper."""

import os

from pathlib import Path

import urgap


class CytoClusterRoutineGating(urgap.unode.UNodeBase):
    """Urgap wrapper for the Routine Gating script of the CytoCluster Pipeline."""

    _path = "Cytocluster/scripts/3_routine_gating.R"

    META_INFO = {
        "name": "CytoClusterRoutineGating",
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
            urgap.uftypes.flow_cytometry.FCS: {"min": 1, "max": 1},
            urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_STRAT_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_STATS_TSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.FCS: {
                "min": 0,
                "max": -1,
            },
            urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_MARKER_EXPRESSION_HTML: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_MARKER_EXPRESSION_TSV: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_JPG: {
                "min": 0,
                "max": -1,
            },
        },
        "engine": None,
        "engine_type": ("flow_cytometry", "qc"),
        "citation": """
        Stefano Pirro
        """,
    }

    def __init__(self) -> None:
        """Initialize cytocluster_routine_gating class."""
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
        input_groups = utrace.input_files.get_path_object_groups_by_uftypes()
        utrace.urun_dict.command_list.extend(["Rscript", str(self.exe_path)])
        for parameter_key in utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ]:
            if parameter_key == "--fcs":
                utrace.urun_dict.command_list.extend(
                    [
                        parameter_key,
                        str(input_groups[urgap.uftypes.flow_cytometry.FCS][0]),
                    ],
                )
            elif parameter_key == "--gatingStrategy":
                utrace.urun_dict.command_list.extend(
                    [
                        parameter_key,
                        str(
                            input_groups[
                                urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_STRAT_CSV
                            ][0],
                        ),
                    ],
                )
            elif parameter_key == "--outDir":
                utrace.urun_dict.command_list.extend(
                    [parameter_key, str(utrace.output_files[0].path.parent)],
                )

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for cytocluster_routine_gating wrapper.

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
        return self.create_command_list(utrace=utrace)

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for cytocluster_routine_gating wrapper.

            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        os.chdir(utrace.urun_dict["old_dir"])
        input_fcs_name = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.flow_cytometry.FCS,
        )[0].stem
        base_name = (
            utrace.output_files[0].path.parent / "routine_gating" / input_fcs_name
        )
        jpgs = Path.glob(str(base_name / "*.jpg"))
        jpgs = [j for j in jpgs if "_tmp_" not in j]
        gating_was_performed = False
        with utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_STRAT_CSV,
        )[0].open() as file:
            gated_types = [row.split(",")[0] for row in file]
        for _i, gated_type in enumerate(gated_types):
            if (base_name / (input_fcs_name + f"_{gated_type}.fcs")).exists():
                gating_was_performed = True
                utrace.extend_output_files_by_uftype(
                    uftype=urgap.uftypes.flow_cytometry.FCS,
                )
                fcs_file = utrace.output_files[-1].path
                utrace.extend_output_files_by_uftype(
                    uftype=urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_JPG,
                )
                jpg_file = utrace.output_files[-1].path
                Path.rename(
                    src=base_name / (input_fcs_name + f"_{gated_type}.fcs"),
                    dst=fcs_file,
                )
                Path.rename(
                    src=next(j for j in jpgs if gated_type.lower() + "_" in j),
                    dst=jpg_file,
                )
        Path.rename(
            src=base_name / "gating_stats.tsv",
            dst=utrace.output_files.get_path_objects_by_uftype(
                urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_STATS_TSV,
            )[0],
        )
        if gating_was_performed is True:
            utrace.extend_output_files_by_uftype(
                uftype=urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_MARKER_EXPRESSION_TSV,
            )
            Path.rename(
                src=base_name / "markers_expression.tsv",
                dst=utrace.output_files[-1].path,
            )
            utrace.extend_output_files_by_uftype(
                uftype=urgap.uftypes.flow_cytometry.qc.gating.CYTOCLUSTER_MARKER_EXPRESSION_HTML,
            )
            Path.rename(
                src=base_name / "markers_expression.html",
                dst=utrace.output_files[-1].path,
            )
        return utrace
