"""Urgap CompressToTar wrapper."""

import json
import shutil

from pathlib import Path

import urgap


class CompressToTar(urgap.unode.UNodeBase):
    """Urgap wrapper for the CompressToTar resource.

    This class allows to tar compress a UFileList of UFiles and Tags.
    """

    META_INFO = {
        "name": "CompressToTar",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "1.0.0", "exe_path": "Compressor/1_0_0/compressor.py"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {urgap.uftypes.any.ANY: {"min": 1, "max": -1}},
        "output_uftypes": {urgap.uftypes.compression.TAR: {"min": 1, "max": -1}},
        "engine": None,
        "engine_type": ("io",),
        "citation": "Urgap team (2022)",
        "parameter_examples": "{}",
    }

    def __init__(self) -> None:
        """Initialize CompressToTar class."""
        super().__init__()

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for CompressToTar wrapper.

        Maximum output tar file size can be defined using -s in parameters.

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
            urgap.uftypes.compression.TAR,
        )[0]

        utrace.urun_dict.command_list = ["python", str(self.exe_path)]
        for file in input_files:
            utrace.urun_dict.command_list.extend(["-i", str(file)])
        for k, v in utrace.urun_dict["parameters"][
            self.META_INFO["unode_full_identifier"]
        ].items():
            utrace.urun_dict.command_list.extend([k, v])
        utrace.urun_dict.command_list.extend(
            [
                "-o",
                str(output_file),
                "-cf",
                "tar",
            ],
        )

        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for CompressToTar wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        if (
            utrace.urun_dict["parameters"][self.META_INFO["unode_full_identifier"]].get(
                "-s",
                None,
            )
            is not None
        ):
            output_file = utrace.output_files.get_path_objects_by_uftype(
                urgap.uftypes.compression.TAR,
            )[0]
            split_tars = [
                file
                for file in Path.iterdir(output_file.parent)
                if file.name.startswith("part.")
            ]
            self._rename_and_extend_safely(
                utrace,
                sorted(split_tars),
                urgap.uftypes.compression.TAR,
            )
        return utrace

    def _rename_and_extend_safely(
        self,
        utrace: urgap.UTrace,
        split_tars: list,
        uftype: str,
    ) -> urgap.UTrace:
        """Extend output file list if any file exists and rename it appropriately.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
            split_tars: List of paths to split tars.
            uftype: Urgap uftype.
        """
        dst = utrace.output_files.get_path_objects_by_uftype(uftype)[0]
        shutil.move(src=split_tars[0], dst=dst)
        for source_file in split_tars[1:]:
            if source_file.exists():
                utrace.extend_output_files_by_uftype(uftype)
                shutil.move(src=source_file, dst=utrace.output_files[-1].path)
        return utrace