"""Urgap extract_scans_3_0_0 wrapper."""

import urgap


class ExtractScans(urgap.unode.UNodeBase):
    """Urgap wrapper for the extract_scans_3_0_0 resource.

    This wrapper calls the main resource from simepy package to extract peak information
    from an input mzml file.
    """

    META_INFO = {
        "name": "extract_scans_3_0_0",
        "version": "3.0.",
        "release_date": "04.06.2023",
        "api_port": 42503,
        "engine_type": (
            "data_extractor",
            "ms",
        ),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 1},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "extract_scan_data.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/extract_scans_3_0_0.zip",
                    "urn_md5": "3626fff4879baa9b7fece4723e44439b",
                    "external_url": "https://raw.githubusercontent.com/computational-ms/simepy/main/example_scripts/extract_scan_data.py",
                    "external_md5": "cf608b984a51a5a5e6f0a0e3a279a00c",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "simepy",
                ],
            },
        },
        "input_uftypes": {
            urgap.uftypes.any.MZML: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.SCANS_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "extract_scans_style_1",
        "citation": "Urgap team (2023)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize extract_scans_3_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for extract_scans_3_0_0 wrapper.

        Prepares the cmd to execute with the extract_scans resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        mzml_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.any.MZML,
        )[0]
        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SCANS_CSV,
        )[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(mzml_file),
            "-o",
            str(self.output_file),
        ]
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight."""
        urgap.ucore.set_column_value(
            self.output_file,
            "filename",
            utrace.input_files[0].object_name,
        )
        return utrace
