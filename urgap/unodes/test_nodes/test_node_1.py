"""TestNode for Rerun logic."""




    META_INFO = {
        "name": "TestNode1",
        "versions": [
            {
                "version": "1.0.0",
                "exe_path": "TestNodes/TestNode1/1_0_0/test_resource_1.py",
        ],
        "parameters_not_triggering_rerun": ["no_rerun_node_trigger", "triggers_nuttin"],
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "engine": None,
        "engine_type": ("test_engine",),
        "input_uftypes": {
        },
        "output_uftypes": {
        },
    }

        """Initialize VennDiagram_1_1_0 class."""

    def preflight(
        self,
        """Preflight routine for TestNode1:1.0.0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "--params",
            utrace.urun_dict.parameters,
            "--input",
        ]
        for ufile in utrace.input_files:
            utrace.urun_dict.command_list.append(str(ufile.path))
        utrace.urun_dict.command_list.append("--output")
        for ufile in utrace.output_files:
            utrace.urun_dict.command_list.append(str(ufile.path))
        return utrace

    def execute(
        self,
        """Execute routine for TestNode1:1.0.0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        super().execute(utrace)

        return utrace

    def postflight(
        self,
        """Preflight routine for TestNode1:1.0.0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.output_files[-1].path.write_text("Writing into 3_of_N")
        return utrace