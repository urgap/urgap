"""TestNode for basic function."""



    META_INFO = {
        "name": "BasicFunctionTestNode",
        "versions": [
        ],
        "parameters_not_triggering_rerun": [
            "cpu",
            "triggers_nuttin",
        ],
        "engine": None,
        "engine_type": ("test_engine",),
        "input_uftypes": {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
                "min": 1,
                "max": 1,
            },
        },
    }

        """Initialize BasicFunctionTestNode class."""

        """Execute routine for BasicFunctionTestNode.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        super().execute(utrace)
        return utrace

        """Preflight routine for BasicFunctionTestNode.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
        ]
        utrace.urun_dict.command_list.append("--output")
        for ufile in utrace.output_files:
            utrace.urun_dict.command_list.append(str(ufile.path))
        return utrace