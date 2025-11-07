"""TestNode for basic function."""

import urgap


class BasicFunctionTestNode(urgap.unode.UNodeBase):
    """Urgap Node for basic function calling the date command."""

    META_INFO = {
        "name": "BasicFunctionTestNode",
        "versions": [
            {
                "version": "0.0.5",
                "exe_path": "BasicFunctionTestNode/0_0_5/basic_function.py",
            },
        ],
        "parameters_not_triggering_rerun": [
            "cpu",
            "triggers_nuttin",
        ],
        "wrapper_version": {"major": 4, "minor": 2, "patch": 0},
        "engine": None,
        "engine_type": ("test_engine",),
        "is_old": True,
        "input_uftypes": {
            urgap.uftypes.test.TEST_FILE1: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.test.TEST_FILE2: {
                "min": 1,
                "max": 1,
            },
        },
        "citation": "Urgap team (2025)",
    }

    def __init__(self) -> None:
        """Initialize BasicFunctionTestNode class."""
        super().__init__()

    def execute(self, utrace: urgap.UTrace) -> urgap.UTrace:
        """Execute routine for BasicFunctionTestNode.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        super().execute(utrace)
        return utrace

    def preflight(self, utrace: urgap.UTrace) -> urgap.UTrace:
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
