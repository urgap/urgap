"""Urgap pymx_normalize_ion_injection_time_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap


class pymx_normalize_ion_injection_time_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_normalize_ion_injection_time_1_0_0 resource.

    This wrapper calls the main resource to normalize peak intensity based on ion
    injection time.
    """

    META_INFO = {
        "name": "pymx_normalize_ion_injection_time_1_0_0",
        "version": "1.0.0",
        "release_date": "03.05.2022",
        "api_port": 42314,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "normalize_ion_injection_time_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_normalize_ion_injection_time_1_0_0.zip",
                    "urn_md5": "db67cd6b6aa0c102979ac4bbf28b4e92",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/normalize_ion_injection_time_1_0_0.py",
                    "external_md5": "4b51314f20e91a8c58bd25078093c321",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ["pymx"],
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.SCANS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.SPECTRA_META_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.NORM_IT_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "normalize_ion_injection_time_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_normalize_ion_injection_time_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_normalize_ion_injection_time_1_0_0 wrapper.

        Prepares the cmd to execute with the normalize_ion_injection_time_1_0_0
        resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.scans_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SCANS_CSV,
        )[0]
        self.metadata_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SPECTRA_META_CSV,
        )[0]
        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.NORM_IT_CSV,
        )[0]
        self.max_injection_time = utrace.urun_dict.translations["all_params"][
            "max_injection_time"
        ]["translated_value"]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-si",
            str(self.scans_file),
            "-mdi",
            str(self.metadata_file),
            "-o",
            str(self.output_file),
            "-mit",
            str(self.max_injection_time),
        ]
        return utrace
