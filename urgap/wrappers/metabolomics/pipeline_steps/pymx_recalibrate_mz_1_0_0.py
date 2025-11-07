"""Urgap pymx_recalibrate_mz_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap


class pymx_recalibrate_mz_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_recalibrate_mz_1_0_0 resource.

    This wrapper calls the main resource to recalibrate the mz value based on
    theoretical mz values of ref masses.
    """

    META_INFO = {
        "name": "pymx_recalibrate_mz_1_0_0",
        "version": "1.0.0",
        "release_date": "05.05.2022",
        "api_port": 42315,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "recalibrate_mz_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_recalibrate_mz_1_0_0.zip",
                    "urn_md5": "2a83676f23eeff79124777804fd5ae46",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/recalibrate_mz_1_0_0.py",
                    "external_md5": "a45212ad8ab499e0de12a77a3f3cc4ec",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ["pymx"],
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.AVG_SCANS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.mx.REF_MASS_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.RECAL_MZ_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "recalibrate_mz_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_recalibrate_mz_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_recalibrate_mz_1_0_0 wrapper.

        Prepares the cmd to execute with the recalibrate_mz_1_0_0 resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.AVG_SCANS_CSV,
        )[0]
        self.refmass_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.mx.REF_MASS_CSV,
        )[0]
        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.RECAL_MZ_CSV,
        )[0]
        self.match_mass_tolerance = utrace.urun_dict.translations["all_params"][
            "match_mass_tolerance"
        ]["translated_value"]
        self.ion_mode = utrace.urun_dict.translations["all_params"]["ion_mode"][
            "translated_value"
        ]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(self.input_file),
            "-ri",
            str(self.refmass_file),
            "-o",
            str(self.output_file),
            "-lt",
            str(self.match_mass_tolerance),
            "-pol",
            str(self.ion_mode),
        ]
        return utrace
