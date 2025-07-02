"""Urgap CompressToZip wrapper."""

import json

from pathlib import Path

import urgap


class CompressToZip(urgap.unode.UNodeBase):
    """Urgap wrapper for the CompressToZip resource.

    This class allows to tar compress a UFileList of UFiles and Tags.
    """

    META_INFO = {
        "name": "CompressToZip",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "1.0.0", "exe_path": "Compressor/1_0_0/compressor.py"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {urgap.uftypes.any.ANY: {"min": 1, "max": -1}},
        "output_uftypes": {urgap.uftypes.compression.ZIP: {"min": 1, "max": -1}},
        "engine": None,
        "engine_type": ("io",),
        "citation": "Urgap team (2022)",
        "parameter_examples": "{}",
    }

    def __init__(self) -> None:
        """Initialize CompressToZip class."""
        super().__init__()

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for CompressToZip wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        input_files = []
        for file in utrace.input_files:
            file_path = Path(file.path)
            tmp_tag_path = file_path.with_suffix(file_path.suffix + ".tag")
            with tmp_tag_path.open("w") as tag_file:
                json.dump(file.tags, tag_file)
            input_files.append((str(file_path), str(tmp_tag_path)))
        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.compression.ZIP,
        )[0]

        utrace.urun_dict.command_list = ["python", str(self.exe_path)]
        for file in input_files:
            utrace.urun_dict.command_list.extend(["-i", str(file)])
        utrace.urun_dict.command_list.extend(
            [
                "-o",
                str(output_file),
                "-cf",
                "zip",
            ],
        )
        return utrace