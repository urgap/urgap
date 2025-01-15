



    """

    META_INFO = {
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
                "min": 1,
                "max": -1,
        },
        "output_uftypes": {
                "min": 1,
                "max": 1,
            },
        },
        "engine": None,
        "engine_type": ("io",),
    }


    def preflight(
        self,

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
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