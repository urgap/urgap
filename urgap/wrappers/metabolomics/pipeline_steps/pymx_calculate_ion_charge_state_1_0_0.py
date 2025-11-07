"""Urgap pymx_calculate_ion_charge_state_1_0_0 wrapper. Part of the MX GSK pipeline."""

import logging

import urgap


class pymx_calculate_ion_charge_state_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the calculate_ion_charge_state_1_0_0 resource.

    This wrapper calls the main resource to calculate the ion charge state based on
    different spacing by 13C isotope distribution.
    """

    META_INFO = {
        "name": "pymx_calculate_ion_charge_state_1_0_0",
        "version": "1.0.0",
        "release_date": "17.06.2022",
        "api_port": 42307,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "calculate_ion_charge_state_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_calculate_ion_charge_state_1_0_0.zip",
                    "urn_md5": "d2ba5255b4d6fc22df8b8b6849587915",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/calculate_ion_charge_state_1_0_0.py",
                    "external_md5": "8a23630ffafb0ded6fa5f55e4a0b70ff",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ["pymx"],
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.MULTI_AVG_SCANS_CSV: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.ms.MERGED_IONS_CSV: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.ms.GLOBAL_RECAL_MZ_CSV: {
                "min": 0,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.ION_CHARGE_STATE_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "calculate_ion_charge_state_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_calculate_ion_charge_state_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_calculate_ion_charge_state_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_files_ls = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.MULTI_AVG_SCANS_CSV,
        )

        self.input_files_ls.extend(
            utrace.input_files.get_path_objects_by_uftype(
                urgap.uftypes.ms.MERGED_IONS_CSV,
            ),
        )

        self.input_files_ls.extend(
            utrace.input_files.get_path_objects_by_uftype(
                urgap.uftypes.ms.GLOBAL_RECAL_MZ_CSV,
            ),
        )

        if len(self.input_files_ls) > 1:
            logging.error(
                f"This node only accepts 1 file of type"
                f"{urgap.uftypes.ms.MULTI_AVG_SCANS_CSV}, "
                f"{urgap.uftypes.ms.MERGED_IONS_CSV} or "
                f"{urgap.uftypes.ms.MERGED_IONS_CSV}. You have provided "
                f"{len(self.input_files_ls)}, which meet the criteria! Check your input! ",
            )
            raise OSError

        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ION_CHARGE_STATE_CSV,
        )[0]
        self.precursor_max_charge = utrace.urun_dict.translations["all_params"][
            "precursor_max_charge"
        ]["translated_value"]
        self.min_adj_peaks = utrace.urun_dict.translations["all_params"][
            "min_adj_peaks"
        ]["translated_value"]
        self.correlation_threshold = utrace.urun_dict.translations["all_params"][
            "correlation_threshold"
        ]["translated_value"]
        self.isotopologue_mass_tolerance = utrace.urun_dict.translations["all_params"][
            "isotopologue_mass_tolerance"
        ]["translated_value"]
        self.ion_mode = utrace.urun_dict.translations["all_params"]["ion_mode"][
            "translated_value"
        ]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(self.input_files_ls[0]),
            "-o",
            str(self.output_file),
            "-ch",
            str(self.precursor_max_charge),
            "-zmers",
            str(self.min_adj_peaks),
            "-corr",
            str(self.correlation_threshold),
            "-tol",
            str(self.isotopologue_mass_tolerance),
            "-pol",
            str(self.ion_mode),
        ]

        return utrace
