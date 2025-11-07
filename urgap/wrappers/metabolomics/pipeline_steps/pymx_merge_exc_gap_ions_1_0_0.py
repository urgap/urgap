"""Urgap pymx_merge_exc_gap_ions_1_0_0 wrapper. Part of the MX GSK pipeline."""

import urgap


class pymx_merge_exc_gap_ions_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_merge_exc_gap_ions_1_0_0 resource.

    This wrapper calls the main resource to merge peaks, which are mutually exclusive.
    A peak is defined as mutually exclusive if it is identified at one mz range, but
    never at a next one. If the peaks are within a defined range, they can be merged
    together.
    """

    META_INFO = {
        "name": "pymx_merge_exc_gap_ions_1_0_0",
        "version": "1.0.0",
        "release_date": "03.06.2022",
        "api_port": 42313,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "merge_exc_gap_ions_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_merge_exc_gap_ions_1_0_0.zip",
                    "urn_md5": "21c4847ee3305571775aea38d91f6608",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/merge_exc_gap_ions_1_0_0.py",
                    "external_md5": "1fbb5936adf966825867bd8cd0fa6faa",
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
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.MERGED_IONS_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "merge_exc_gap_ions_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_merge_exc_gap_ions_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_merge_exc_gap_ions_1_0_0 wrapper.

        Checks and sets the input_path and output_file_path. Subsequently, assembles the
        command_list, which is executed during execute().

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.MULTI_AVG_SCANS_CSV,
        )[0]
        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.MERGED_IONS_CSV,
        )[0]
        self.match_mass_tolerance = utrace.urun_dict.translations["all_params"][
            "match_mass_tolerance"
        ]["translated_value"]
        self.threshold_gap_ions = utrace.urun_dict.translations["all_params"][
            "threshold_gap_ions"
        ]["translated_value"]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(self.input_file),
            "-o",
            str(self.output_file),
            "-md",
            str(self.match_mass_tolerance),
            "-perc_gaps",
            str(self.threshold_gap_ions),
        ]

        return utrace
