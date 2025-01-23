



    Allows to filter and merge multiple csv files based on a pandas query string.
    """

    META_INFO = {
        "name": "FilterTabularToXlsx",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "1.0.0", "exe_path": "FilterTabular/1_0_0/filter_tabular.py"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
                "min": 1,
                "max": 1,
            },
        },
        "engine": None,
        "engine_type": ("io",),
    }

        """Initialize FilterTabularToXlsx class."""

    def preflight(
        self,
        """Preflight routine for FilterTabularToXlsx wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = ["python", str(self.exe_path), "-m", "xlsx"]
        for file in utrace.input_files:
            utrace.urun_dict.command_list.extend(["-i", str(file.path)])

        utrace.urun_dict.command_list.extend(
            [
                "-o",
                str(utrace.output_files[0].path),
        )
        for parameter_key, parameter_value in utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ].items():
            if parameter_value is not None:
                utrace.urun_dict.command_list.extend([parameter_key, parameter_value])

        return utrace