"""Urgap precursor window scanner wrapper."""

import urgap


class precursor_window_scanner_1_0_1(urgap.unode.UNodeBase):
    """precursor_scanner_1_0_1 Urgap Node."""

    META_INFO = {
        "name": "precursor_window_scanner_1_0_1",
        "version": "1.0.1",
        "release_date": "22.02.2022",
        "api_port": 42726,
        "engine_type": ("converter", "proteomics"),
        "platform_independent": True,  # The executable for platform independent is expected to be under
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "precursor_window_scanner_1_0_1.py",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "unimod_mapper",
                ],
            },
        },
        "wrapper_version": {
            "major": 1,
            "minor": 0,
            "patch": 1,
        },
        "input_uftypes": {
            urgap.uftypes.ms.SPECTRA_META_CSV: {"min": 1, "max": 1},
            urgap.uftypes.ms.SCANS_CSV: {"min": 1, "max": 1},
            urgap.uftypes.ms.INSTRUMENT_UNIT_CSV: {"min": 1, "max": 1},
            urgap.uftypes.ms.SPECTRA_NOISE_CSV: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.ms.PRECURSOR_WINDOW_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "precursor_window_scanner_style_1",
        "citation": "Mathieson T. and Sweetman, G. (2021)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize precursor_window_scanner_1_0_1 class."""
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
        scans_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SCANS_CSV,
        )[0]
        spec_meta_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SPECTRA_META_CSV,
        )[0]
        spec_noise_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SPECTRA_NOISE_CSV,
        )[0]
        instrument_meta_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.INSTRUMENT_UNIT_CSV,
        )[0]
        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.PRECURSOR_WINDOW_CSV,
        )[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "--spectrum_meta",
            str(spec_meta_file),
            "--instrument_meta",
            str(instrument_meta_file),
            "--spectrum_noise",
            str(spec_noise_file),
            "--scan_data",
            str(scans_file),
            "--outfile",
            str(output_file),
        ]
        # append additional node params
        for param_dict in utrace.urun_dict.translations[
            "all_params"
        ].values():
            utrace.urun_dict.command_list.extend(
                [param_dict["translated_key"], str(param_dict["translated_value"])],
            )
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight."""
        lineage_roots = utrace.input_files[0].lineage_root_files
        urgap.ucore.set_column_value(
            utrace.output_files[0].path,
            "filename",
            lineage_roots[0],
        )
        return utrace
