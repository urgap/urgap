"""Urgap reporter_correction_1_0_0 wrapper."""

import urgap


class reporter_correction_1_0_0(urgap.unode.UNodeBase):  # noqa
    """Reporter_correction_1_0_0 Urgap Node."""

    META_INFO = {
        "name": "reporter_correction_1_0_0",
        "version": "1.0.0",
        "release_date": "01.10.2022",
        "api_port": 42727,
        "engine_type": ("quantification", "proteomics"),
        "platform_independent": True,  # The executable for platform independent is expected to be under
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "reporter_correction_1_0_0.py",
                    # "zip_md5": "<>",
                },
            },
        },
        "wrapper_version": {
            "major": 1,
            "minor": 0,
            "patch": 0,
        },
        "input_uftypes": {
            # For example: .... please refer to urgap.uftypes for full list...
            urgap.uftypes.proteomics.quantification.reporter_ions.REPORTER_IONS: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.proteomics.TMT_CORRECTION_FACTORS: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            # will be checked after execution if all have been added using unode.add_auxiliary_output_file()
            urgap.uftypes.proteomics.quantification.reporter_ions.ISO_CORRECTED_REPORTER_IONS: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "reporter_correction_style_1",
        "citation": "TM",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize reporter_correction_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Run preflight for wrapper.

        Extracts relevant output and input files to feed to execute

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        reporter_ions_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.quantification.reporter_ions.REPORTER_IONS,
        )[0]
        correction_factor_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.TMT_CORRECTION_FACTORS,
        )[0]

        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.quantification.reporter_ions.ISO_CORRECTED_REPORTER_IONS,
        )[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "--correction_factor_file",
            str(correction_factor_file),
            "--reporter_ions",
            str(reporter_ions_file),
            "--outfile",
            str(output_file),
        ]

        # append additional node params
        for _urgap_name, param_dict in utrace.urun_dict.translations[
            "all_params"
        ].items():
            utrace.urun_dict.command_list.extend(
                [param_dict["translated_key"], str(param_dict["translated_value"])],
            )
        return utrace
