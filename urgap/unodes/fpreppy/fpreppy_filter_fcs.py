"""Urgap FpreppyFilterFCS wrapper."""

import urgap


class FpreppyFilterFCS(urgap.unode.UNodeBase):
    """Urgap wrapper for the fpreppy_filter_fcs resource.

    Allows to filter and merge multiple FCS files based on a pandas query string.
    """

    META_INFO = {
        "name": "FpreppyFilterFCS",
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
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.flow_cytometry.FCS: {
                "min": 1,
                "max": 1,
            },
        },
        "citation": "Urgap team (2024)",
    }

    def __init__(self) -> None:
        """Initialize FpreppyFilterFCS class."""
        super().__init__()

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for FpreppyFilterFCS wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = [self.exe_path, "filter_fcs"]
        comma_separated_input_files = ",".join(
            [str(file.path) for file in utrace.input_files],
        )
        utrace.urun_dict.command_list.extend(["-f", comma_separated_input_files])
        for k, v in utrace.urun_dict.parameters[
            self.META_INFO["unode_full_identifier"]
        ].items():
            utrace.urun_dict.command_list.extend([k, v])
        utrace.urun_dict.command_list.extend(["-o", str(utrace.output_files[0].path)])

        return utrace
