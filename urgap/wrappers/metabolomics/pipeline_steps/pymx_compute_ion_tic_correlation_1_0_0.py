"""Urgap pymx_compute_ion_tic_correlation_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap


class pymx_compute_ion_tic_correlation_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_compute_ion_tic_correlation_1_0_0 resource.

    This wrapper calls the main resource to compute pearson R correlation between the
    ion intensity and total ion current. In addition, it provides information about the
    fraction of scans in which each peak was identified.
    """

    META_INFO = {
        "name": "pymx_compute_ion_tic_correlation_1_0_0",
        "version": "1.0.0",
        "release_date": "05.05.2022",
        "api_port": 42308,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "compute_ion_tic_correlation_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_compute_ion_tic_correlation_1_0_0.zip",
                    "urn_md5": "6ec90a46599f557679cf254938f15443",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/compute_ion_tic_correlation_1_0_0.py",
                    "external_md5": "19aa828dd74a6dc1da63e83d83db62c2",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": ["pymx"],
            },
        },
        "input_uftypes": {
            urgap.uftypes.ms.ALIGN_SCANS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.SPECTRA_META_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.ION_TIC_CORR_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "pymx_compute_ion_tic_correlation_1_0_0",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_compute_ion_tic_correlation_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_compute_ion_tic_correlation_1_0_0 wrapper.

        Prepares the cmd to execute with the compute_ion_tic_correlation_1_0_0 resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ALIGN_SCANS_CSV,
        )[0]
        self.metadata_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SPECTRA_META_CSV,
        )[0]
        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ION_TIC_CORR_CSV,
        )[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(self.input_file),
            "-mdi",
            str(self.metadata_file),
            "-o",
            str(self.output_file),
        ]
        return utrace
