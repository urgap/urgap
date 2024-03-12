



    META_INFO = {
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
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


    def execute(
        self,

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        super().execute(utrace)
        return utrace

    def preflight(
        self,

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = ["python", "-c", "import sys;sys.exit(420)"]
        return utrace