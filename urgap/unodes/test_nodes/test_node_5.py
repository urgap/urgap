



    META_INFO = {
        "name": "TestNode5",
        "versions": [
            {
                "version": "1.0.0",
                "exe_path": "TestNodes/TestNode5/1_0_0/test_resource_5.py",
        ],
        "parameters_not_triggering_rerun": ["no_rerun_node_trigger"],
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "engine": None,
        "engine_type": ("test_engine",),
        "input_uftypes": {
                "min": 0,
                "max": -1,
            },
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
                "min": 0,
                "max": 1,
            },
                "min": 1,
                "max": 9,
            },
                "min": 3,
                "max": 3,
            },
        },
    }

        """Initialize test_node_v9 class."""

    def execute(
        self,
        """Execute routine for TestNode5 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        super().execute(utrace)
        return utrace

    def preflight(
        self,
        """Preflight routine for TestNode5 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        minimal_dataset = utrace.output_files.number_of_uftypes()
        for filetype, n in utrace.urun_dict.parameters[
            self.META_INFO["unode_full_identifier"]
        ].items():
            difference = n - minimal_dataset.get(filetype, 0)
            for _ in range(difference):
                utrace.extend_output_files_by_uftype(uftype=filetype)

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "--params",
            utrace.urun_dict.parameters[self.META_INFO["unode_full_identifier"]],
            "--input",
        ]
        for ufile in utrace.input_files:
            utrace.urun_dict.command_list.append(str(ufile.path))
        utrace.urun_dict.command_list.append("--output")
        for ufile in utrace.output_files:
            utrace.urun_dict.command_list.append(str(ufile.path))
        return utrace