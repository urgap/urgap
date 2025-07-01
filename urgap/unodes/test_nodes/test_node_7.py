"""Urgap TestNode7 wrapper."""

import urgap


class TestNode7(urgap.unode.UNodeBase):
    """Urgap wrapper for TestNode7 resource."""

    META_INFO = {
        "name": "TestNode7",
        "versions": [
            {
                "version": "1.0.0",
                "exe_path": "TestNodes/TestNode6/1_0_0/test_resource_6.py",
            },
        ],
        "parameters_not_triggering_rerun": ["no_rerun_node_trigger"],
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "engine": None,
        "engine_type": ("test_engine",),
        "input_uftypes": {
            urgap.uftypes.test.TEST_FILE2: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.test.TEST_FILE1: {
                "min": 1,
                "max": 1,
            },
        },
        "citation": "Urgap team (2023)",
    }

    def __init__(self) -> None:
        """Initialize test_node_v12 class."""
        super().__init__()

    def execute(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Execute routine for TestNode7 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        super().execute(utrace)
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for TestNode7 wrapper.

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