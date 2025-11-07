"""Urgap pymx_align_scans_dbscan_1_0_0 wrapper. Part of the MX GSK pipeline."""

import logging

import urgap


class pymx_align_scans_dbscan_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymx_align_scans_dbscan_1_0_0 resource.

    This wrapper calls the main resource to align peaks from multiple scans within a
    signle spectrum file.
    """

    META_INFO = {
        "name": "pymx_align_scans_dbscan_1_0_0",
        "version": "1.0.0",
        "release_date": "05.05.2022",
        "api_port": 42302,
        "engine_type": ("metabolomics",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "align_scans_dbscan_1_0_0.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/pymx_align_scans_dbscan_1_0_0.zip",
                    "urn_md5": "a3775192180c337205e45f52e03a849e",
                    "external_url": "https://github.com/gsk-tech/pymx/raw/main/example_scripts/align_scans_dbscan_1_0_0.py",
                    "external_md5": "f7416fdfa44b09d3bac035d931b2c25d",
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
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.ms.NORM_IT_CSV: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.ms.SPECTRA_META_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.ALIGN_SCANS_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "align_scans_dbscan_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymx_align_scans_dbscan_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymx_align_scans_dbscan_1_0_0 wrapper.

        Prepares the cmd to execute with the align_scans_dbscan_1_0_0 resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        self.input_file_list = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SCANS_CSV,
        )

        self.input_file_list.extend(
            utrace.input_files.get_path_objects_by_uftype(urgap.uftypes.ms.NORM_IT_CSV),
        )

        if len(self.input_file_list) > 1:
            logging.error(
                f"You can only provide either {urgap.uftypes.ms.SCANS_CSV} or "
                f"{urgap.uftypes.ms.NORM_IT_CSV} to the node. NOT both simultaneously!",
            )
            raise ValueError

        self.metadata_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SPECTRA_META_CSV,
        )[0]

        self.output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.ALIGN_SCANS_CSV,
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
            str(self.input_file_list[0]),
            "-mdi",
            str(self.metadata_file),
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
