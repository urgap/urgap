"""Urgap Interdock wrapper."""

import urgap


class Interdock(urgap.unode.UNodeBase):
    """Urgap wrapper for the Interdock Pipeline."""

    META_INFO = {
        "name": "Interdock",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {
                "version": "0.5.0",
                "exe_path": "$interdock",
            },
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.molecular_structure.ANY: {"min": 1, "max": 1},
            urgap.uftypes.interdock.model.ANY: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.interdock.LOG: {"min": 1, "max": -1},
            urgap.uftypes.interdock.CONFIG: {"min": 1, "max": -1},
            urgap.uftypes.interdock.OUT: {"min": 1, "max": -1},
        },
        "engine": None,
        "engine_type": ("interdock",),
        "citation": """
            GSK Internal
            (Yves Simenya)
        """,
    }

    def __init__(self) -> None:
        """Initialize Interdock class."""
        super().__init__()
        self.output_dir = None

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for Interdock wrapper.

        During preflight,
            - parameters are formatted
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list.extend(["interdock", "-st", "240", "-o"])
        self.output_dir = str(urgap.scratch_disk_base / "interdock_output")
        utrace.urun_dict.command_list.append(self.output_dir)
        for file in utrace.input_files:
            match file.uftype:
                case urgap.uftypes.molecular_structure.PROTEIN:
                    utrace.urun_dict.command_list.extend(["-i", str(file.path)])
                case urgap.uftypes.molecular_structure.POLYSACC:
                    utrace.urun_dict.command_list.extend(["-i", str(file.path)])
                case urgap.uftypes.interdock.model.PDBQT:
                    utrace.urun_dict.command_list.extend(["-t", str(file.path)])
                case urgap.uftypes.interdock.model.PDB:
                    utrace.urun_dict.command_list.extend(["-t", str(file.path)])
        for k, v in utrace.urun_dict["parameters"][
            self.META_INFO["unode_full_identifier"]
        ].items():
            if k == "-s":
                utrace.urun_dict.command_list.append(k)
            else:
                utrace.urun_dict.command_list.extend([k, v])
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for Interdock wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        output_dir = next(
            (
                folder
                for folder in list(urgap.scratch_disk_base.iterdir())
                if str(folder).startswith(self.output_dir)
            ),
            None,
        )
        all_files = [f for f in output_dir.rglob("*") if f.is_file()]
        log_files = list(output_dir.rglob("*.log"))
        utrace.move_output_files(
            files=log_files,
            uftype=urgap.uftypes.interdock.LOG,
            extend_len=len(log_files) - 1,
        )
        out_files = list(output_dir.rglob("*.out"))
        utrace.move_output_files(
            files=out_files,
            uftype=urgap.uftypes.interdock.OUT,
            extend_len=len(out_files) - 1,
        )
        config_files = list(set(all_files) - set(log_files) - set(out_files))
        utrace.move_output_files(
            files=config_files,
            uftype=urgap.uftypes.interdock.CONFIG,
            extend_len=len(config_files) - 1,
        )
        return utrace
