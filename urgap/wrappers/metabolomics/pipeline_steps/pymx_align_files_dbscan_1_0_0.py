"""Urgap pymx_align_files_dbscan_1_0_0 wrapper. Part of the MX GSK pipeline."""

import logging

import urgap


class pymx_align_files_dbscan_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_align_files_dbscan_1_0_0 resource.

    This wrapper calls the main resource to align peaks across multiple files.
    """

    META_INFO = {
        "name": "pymx_align_files_dbscan_1_0_0",
        "version": "1.0.0",
        "release_date": "05.05.2022",
        "api_port": 42301,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "align_files_dbscan_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_align_files_dbscan_1_0_0.zip",
                    "urn_md5": "1208eeee120021f04375c687d26a5b15",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/align_files_dbscan_1_0_0.py",
                    "external_md5": "192f1fe729084b58d154120d8f131b65",
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
                "min": 0,
                "max": -1,
            },
            urgap.uftypes.ms.RECAL_MZ_CSV: {
                "min": 0,
                "max": -1,
            },
            urgap.uftypes.ms.ION_TIC_CORR_CSV: {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.MULTI_ALIGN_SCANS_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "align_files_dbscan_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_align_files_dbscan_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_align_files_dbscan_1_0_0 wrapper.

        Checks and sets the input_path, tic_path_file and output_file_path.
        Subsequently, assembles the command_list, which is executed during execute().

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_file_list = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.AVG_SCANS_CSV,
        )
        self.input_file_list.extend(
            utrace.input_files.get_path_objects_by_uftype(
                urgap.uftypes.ms.RECAL_MZ_CSV,
            ),
        )

        if len(self.input_file_list) < 2:
            logging.error(
                f"You have provided only {len(self.input_file_list)} valid files. This "
                f"node "
                f"requires at least 2 files, of the of type"
                f" {urgap.uftypes.ms.AVG_SCANS_CSV} or {urgap.uftypes.ms.RECAL_MZ_CSV}"
                f" to align peaks across them!",
            )
            raise OSError

        # TODO: include check that you should not provide either or and mix them!

        self.tic_corr_file_list = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ION_TIC_CORR_CSV,
        )

        if len(self.input_file_list) != len(self.tic_corr_file_list):
            logging.error(
                f"You have provided {len(self.input_file_list)} input files and"
                f" {len(self.tic_corr_file_list)} files with ion-tic correlation "
                f"information. "
                f"Both lists should have the same length, as the corresponding files "
                f"will be merged together to assemble a dataframe containing full "
                f"information.",
            )
            raise OSError

        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.MULTI_ALIGN_SCANS_CSV,
        )[0]
        self.fraction_detected_ions = utrace.urun_dict.translations["all_params"][
            "fraction_detected_ions"
        ]["translated_value"]
        self.cluster_n_neighbours = utrace.urun_dict.translations["all_params"][
            "cluster_n_neighbours"
        ]["translated_value"]
        self.max_distance = utrace.urun_dict.translations["all_params"][
            "cluster_max_distance"
        ]["translated_value"]
        self.distance_metric = utrace.urun_dict.translations["all_params"][
            "cluster_distance_metric"
        ]["translated_value"]
        self.n_jobs = utrace.urun_dict.translations["all_params"]["cpus"][
            "translated_value"
        ]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            *[str(file) for file in self.input_file_list],
            "-tici",
            *[str(file) for file in self.tic_corr_file_list],
            "-o",
            str(self.output_file),
            "-msf",
            str(self.fraction_detected_ions),
            "-msn",
            str(self.cluster_n_neighbours),
            "-e",
            str(self.max_distance),
            "-m",
            str(self.distance_metric),
            "-nj",
            str(self.n_jobs),
        ]

        return utrace
