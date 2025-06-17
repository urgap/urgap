



    Creates Venn Diagram SVG graphics from 1-n csv files.
    """

    META_INFO = {
        "name": "VennDiagram",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "2.0.0", "exe_path": "VennDiagram/2_0_0/venn_diagram.py"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
                "min": 1,
                "max": -1,
        },
        "output_uftypes": {
                "min": 1,
                "max": 1,
            },
            #     "min": 1,  # noqa: ERA001
            #     "max": 1,  # noqa: ERA001
            # }, # Not implemented yet. Will be as soon someone needs it
        },
        "engine": None,
        "engine_type": ("plotter",),
        "parameter_examples": """
            {
                "--id-column": "<id-name>" #  Column used to group data
                "--value-column": "<calue-name>" # Column for data value
                # both kwargs can also be a list if multiple columns should be concatenated.
                "--header": "My Venn Diagram"
            }
        """,
    }

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Initialize VennDiagram."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        """Preflight routine for VennDiagram wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = ["python", str(self.exe_path)]
        for ifile in utrace.input_files:
            utrace.urun_dict.command_list.extend(["--csv-file", str(ifile.path)])

        utrace.urun_dict.command_list.extend(
            [
                "--output-file",
                str(utrace.output_files[0].path),
        )
        for parameter_key, parameter_value in utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ].items():
            if isinstance(parameter_value, list):
                for _ in parameter_value:
                    utrace.urun_dict.command_list.extend([parameter_key, _])
            else:
                utrace.urun_dict.command_list.extend([parameter_key, parameter_value])

        return utrace