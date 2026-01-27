"""Urgap TestNode2 wrapper."""

import urgap


class TestNode2(urgap.unode.UNodeBase):
    """Urgap wrapper for TestNode2 resource."""

    META_INFO = {
        "name": "TestNode2",
        "versions": [
            {
                "version": "1.0.0",
                "exe_path": "TestNodes/TestNode2/1_0_0/test_resource_2.py",
            },
        ],
        "parameters_not_triggering_rerun": ["no_rerun_node_trigger"],
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "engine": None,
        "engine_type": ("test_engine",),
        "input_uftypes": {
            urgap.uftypes.test.TEST_FILE1: {"min": 1, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.test.TEST_FILE1: {"min": 0, "max": 1},
            urgap.uftypes.test.TEST_FILE2: {"min": 1, "max": 9},
            urgap.uftypes.test.TEST_FILE3: {"min": 3, "max": 3},
            urgap.uftypes.test.TEST_FILE4: {"min": 0, "max": -1},
        },
        "citation": "Urgap team (2021)",
    }

    def __init__(self) -> None:
        """Initialize TestNode2 class."""
        super().__init__()

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
        return utrace
