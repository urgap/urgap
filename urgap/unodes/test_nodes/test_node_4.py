"""Urgap TestNode4 wrapper."""

import urgap


class TestNode4(urgap.unode.UNodeBase):
    """Urgap wrapper for TestNode4 resource."""

    META_INFO = {
        "name": "TestNode4",
        "versions": [
            {
                "version": "1.0.0",
                "exe_path": "TestNodes/TestNode4/1_0_0/test_resource_4.py",
            },
        ],
        "parameters_not_triggering_rerun": ["no_rerun_node_trigger"],
        "wrapper_version": {"major": "x", "minor": "x", "patch": "x"},
        "engine": None,
        "engine_type": ("test_engine",),
        "input_uftypes": {
            urgap.uftypes.test.ANY: {
                "min": 2,
                "max": 4,
            },
        },
        "output_uftypes": {
            urgap.uftypes.test.TEST_FILE1: {
                "min": 2,
                "max": -1,
            },
        },
        "citation": "Urgap team (2021)",
    }

    def __init__(self) -> None:
        """Initialize TestNode4 class."""
        super().__init__()

    def execute(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Execute routine for TestNode4 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        return utrace
