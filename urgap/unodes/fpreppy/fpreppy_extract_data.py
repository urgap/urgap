"""Urgap FpreppyExtractData wrapper."""

import urgap


class FpreppyExtractData(urgap.unode.UNodeBase):
    """Urgap wrapper for the FpreppyExtractData resource."""

    META_INFO = {
        "name": "FpreppyExtractData",
        "versions": [
            {"version": "1.0.0", "exe_path": "$fpreppy"},
        ],
        "parameters_not_triggering_rerun": [],
        "engine": None,
        "engine_type": ("flow_cytometry", "io"),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "input_uftypes": {
            urgap.uftypes.flow_cytometry.FCS: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.gating_strategy.ANY: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.meta.FPREPPY_EXP_METADATA_XLSX: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.meta.FPREPPY_PLATE_METADATA_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.meta.MARKER_MAPPING_JSON: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.meta.GATE_MAPPING_JSON: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.meta.ADDITONAL_MAPPING_JSON: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.meta.OMIQ_GATE_BOOLEAN_FILE: {
                "min": 0,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.flow_cytometry.stats.STATS_PARQUET: {
                "min": 1,
                "max": -1,
            },
        },
        "citation": "Urgap team (2025)",
    }

    def __init__(self) -> None:
        """Initialize FpreppyExtractData class."""
        super().__init__()

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for FpreppyExtractData wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = [self.exe_path, "export_data"]
        uftype_path_groups = utrace.input_files.get_path_object_groups_by_uftypes()
        gating_strategy = _get_gating_strategy(uftype_path_groups=uftype_path_groups)
        utrace.urun_dict.command_list.extend(
            [
                "-f",
                uftype_path_groups[urgap.uftypes.flow_cytometry.FCS][0],
            ],
        )
        if gating_strategy == urgap.uftypes.flow_cytometry.gating_strategy.OMIQ_GFILE:
            utrace.urun_dict.command_list.extend(
                [
                    "-g",
                    uftype_path_groups[gating_strategy][0],
                    "-p",
                    uftype_path_groups[
                        urgap.uftypes.flow_cytometry.meta.OMIQ_GATE_BOOLEAN_FILE
                    ][0],
                ],
            )
        else:
            utrace.urun_dict.command_list.extend(
                [
                    "-g",
                    uftype_path_groups[gating_strategy][0],
                ],
            )
        utrace.urun_dict.command_list.extend(
            [
                "-x",
                uftype_path_groups[
                    urgap.uftypes.flow_cytometry.meta.FPREPPY_EXP_METADATA_XLSX
                ][0],
            ],
        )
        utrace.urun_dict.command_list.extend(
            [
                "-c",
                uftype_path_groups[
                    urgap.uftypes.flow_cytometry.meta.FPREPPY_PLATE_METADATA_CSV
                ][0],
            ],
        )
        if urgap.uftypes.flow_cytometry.meta.MARKER_MAPPING_JSON in uftype_path_groups:
            utrace.urun_dict.command_list.extend(
                [
                    "-j",
                    uftype_path_groups[
                        urgap.uftypes.flow_cytometry.meta.MARKER_MAPPING_JSON
                    ][0],
                ],
            )
        if urgap.uftypes.flow_cytometry.meta.GATE_MAPPING_JSON in uftype_path_groups:
            utrace.urun_dict.command_list.extend(
                [
                    "-t",
                    uftype_path_groups[
                        urgap.uftypes.flow_cytometry.meta.GATE_MAPPING_JSON
                    ][0],
                ],
            )
        if (
            urgap.uftypes.flow_cytometry.meta.ADDITONAL_MAPPING_JSON
            in uftype_path_groups
        ):
            utrace.urun_dict.command_list.extend(
                [
                    "-a",
                    uftype_path_groups[
                        urgap.uftypes.flow_cytometry.meta.ADDITONAL_MAPPING_JSON
                    ][0],
                ],
            )
        for k, v in utrace.urun_dict.parameters[
            self.META_INFO["unode_full_identifier"]
        ].items():
            utrace.urun_dict.command_list.extend([k, v])
        self._output_dir = utrace.output_files[0].path.parent / utrace.output_files_stem
        utrace.urun_dict.command_list.extend(["-o", str(self._output_dir)])
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for FpreppyExtractData wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        for i, parquet_file in enumerate(self._output_dir.glob("*.parquet")):
            if i == 0:
                parquet_file.rename(utrace.output_files[0].path)
            else:
                utrace.extend_output_files_by_uftype(
                    urgap.uftypes.flow_cytometry.stats.STATS_PARQUET,
                )
                parquet_file.rename(utrace.output_files[-1].path)
            utrace.output_files[-1].tags["original_file_name"] = parquet_file.name
        return utrace


def _get_gating_strategy(
    uftype_path_groups: dict,
) -> urgap.UTrace:
    process_uftypes_lookup_list = [
        leafs[1]
        for leafs in urgap.instances.utree_querier.get_leafs_from_node(
            node=urgap.uftypes.flow_cytometry.gating_strategy.ANY,
        )
    ]
    gating_strategy_uftype = [
        uftype for uftype in process_uftypes_lookup_list if uftype in uftype_path_groups
    ]
    if len(gating_strategy_uftype) != 1:
        msg = f"Only one gating_strategy input file eligible. Found {len(gating_strategy_uftype)}"
        raise ValueError(msg)
    return gating_strategy_uftype[0]
