"""Urgap Beacon wrapper."""

import os

from pathlib import Path

import urgap


class Beacon(urgap.unode.UNodeBase):
    """Urgap wrapper for the Beacon Pipeline."""

    META_INFO = {
        "name": "Beacon",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {
                "version": "1.0.0",
                "exe_path": "$bip",
            },
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.beacon.IMAGE_TIFF: {"min": 1, "max": -1},
            urgap.uftypes.beacon.ESSAY_XML: {"min": 1, "max": 1},
            urgap.uftypes.beacon.OPTOSELECT_XML: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.beacon.MLSUMMARY_PARQUET: {"min": 1, "max": 1},
            urgap.uftypes.beacon.MLRAW_PARQUET: {"min": 1, "max": 1},
            urgap.uftypes.beacon.SUMMARY_PARQUET: {"min": 1, "max": 1},
            urgap.uftypes.beacon.BRIGHTFIELD_SUMMARY_PARQUET: {"min": 1, "max": 1},
            urgap.uftypes.beacon.RESULT_PNG: {"min": 0, "max": -1},
        },
        "engine": None,
        "engine_type": ("beacon",),
        "citation": """
            GSK Internal
            (Pavlos Kotidis, John Craven, Matthew Haines, Zachary Inglis, Siofra Murdoch, Mathew Chacko, Raaz Gurung)
        """,
    }

    def __init__(self) -> None:
        """Initialize Beacon class."""
        super().__init__()
        self.device_id = None
        self.old_work_dir = None

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for Beacon wrapper.

        During preflight,
            - parameters are formatted
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.old_work_dir = Path.cwd()
        utrace.urun_dict.command_list.extend(["bip", "run", "."])
        for k, v in utrace.urun_dict["parameters"][
            self.META_INFO["unode_full_identifier"]
        ].items():
            if k == "-id":
                self.device_id = v
            utrace.urun_dict.command_list.extend([k, v])
        if (urgap.scratch_disk / "DataSessions").exists() is False:
            msg = "DataSessions folder does not exist."
            raise RuntimeError(msg)
        os.chdir(urgap.scratch_disk / "DataSessions")
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for Beacon wrapper.

            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        out_dir = urgap.scratch_disk / "DataSessions" / self.device_id
        parquet_files = [
            file for file in out_dir.iterdir() if file.suffix == ".parquet"
        ]
        thumbnails_dir = out_dir / "Processed Data" / "Thumbnails"
        png_files = list(thumbnails_dir.rglob("*.png"))
        for o_file in parquet_files:
            if o_file.stem == "mlsummary":
                utrace.move_output_files(
                    files=[o_file],
                    uftype=urgap.uftypes.beacon.MLSUMMARY_PARQUET,
                )
            elif o_file.stem == "mlraw":
                utrace.move_output_files(
                    files=[o_file],
                    uftype=urgap.uftypes.beacon.MLRAW_PARQUET,
                )
            elif o_file.stem == "summary":
                utrace.move_output_files(
                    files=[o_file],
                    uftype=urgap.uftypes.beacon.SUMMARY_PARQUET,
                )
            elif o_file.stem == "brightfield_summary":
                utrace.move_output_files(
                    files=[o_file],
                    uftype=urgap.uftypes.beacon.BRIGHTFIELD_SUMMARY_PARQUET,
                )
        number_png_files = len(png_files)
        utrace.move_output_files(
            files=png_files,
            uftype=urgap.uftypes.beacon.RESULT_PNG,
            extend_len=number_png_files,
            keep_original_name=True,
        )

        os.chdir(self.old_work_dir)
        return utrace
