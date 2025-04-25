



    META_INFO = {
        "name": "TestNode4",
        "versions": [
            {
                "version": "1.0.0",
                "exe_path": "TestNodes/TestNode4/1_0_0/test_resource_4.py",
        ],
        "parameters_not_triggering_rerun": ["no_rerun_node_trigger"],
        "wrapper_version": {"major": "x", "minor": "x", "patch": "x"},
        "engine": None,
        "engine_type": ("test_engine",),
        "input_uftypes": {
                "min": 2,
                "max": 4,
            },
        },
        "output_uftypes": {
                "min": 2,
                "max": -1,
            },
        },
    }

    def __init__(self) -> None:
        """Initialize TestNode4 class."""
        super().__init__()

    def execute(
        self,
        """Execute routine for TestNode4 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        return utrace