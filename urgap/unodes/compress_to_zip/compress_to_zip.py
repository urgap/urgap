
import json




    This class allows to tar compress a UFileList of UFiles and Tags.
    """

    META_INFO = {
        "name": "CompressToZip",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "1.0.0", "exe_path": "Compressor/1_0_0/compressor.py"},
        ],
        "parameters_not_triggering_rerun": [],
        "engine": None,
        "engine_type": ("io",),
    }

    def __init__(self) -> None:
        """Initialize CompressToZip class."""
        super().__init__()

    def preflight(
        self,
        """Preflight routine for CompressToZip wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        input_files = []
        for file in utrace.input_files:
            with tmp_tag_path.open("w") as tag_file:
        output_file = utrace.output_files.get_path_objects_by_uftype(
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