"""TestNode for Rerun logic."""

import urgap


class TestNode1(urgap.unode.UNodeBase):
    """Urgap wrapper for TestNode1:1.0.0 resource."""

    META_INFO = {
        "name": "TestNode1",
        "versions": [
            {
                "version": "1.0.0",
                "exe_path": "TestNodes/TestNode1/1_0_0/test_resource_1.py",
            },
        ],
        "parameters_not_triggering_rerun": ["no_rerun_node_trigger", "triggers_nuttin"],
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "engine": None,
        "engine_type": ("test_engine",),
        "input_uftypes": {
            urgap.uftypes.test.TEST_FILE1: {"min": 1, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.test.TEST_FILE2: {"min": 1, "max": -1},
        },
        "citation": "Urgap team (2021)",
    }

    def __init__(self) -> None:
        """Initialize VennDiagram_1_1_0 class."""
        super().__init__()

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for TestNode1:1.0.0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.extend_output_files_by_uftype(urgap.uftypes.test.TEST_FILE2)
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
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
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
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for TestNode1:1.0.0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.extend_output_files_by_uftype(urgap.uftypes.test.TEST_FILE2)
        utrace.output_files[-1].path.write_text("Writing into 3_of_N")
        return utrace
