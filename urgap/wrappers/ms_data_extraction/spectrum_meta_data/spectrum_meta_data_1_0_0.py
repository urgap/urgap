"""Urgap spectrum_meta_data_1_0_0 wrapper."""

import logging

import urgap


class ExtractSpectrumMetaData(urgap.unode.UNodeBase):
    """Urgap wrapper for the spectrum_meta_data_1_0_0 resource.

    This wrapper calls the extract_meta_data resource from simepy package to extract
    peak information from an input raw or mzml file. Note: for raw_file extraction the
    cz_xcalibur package is required.
    """

    META_INFO = {
        "name": "spectrum_meta_data_1_0_0",
        "version": "1.0.0",
        "release_date": "14.04.2023",
        "api_port": 42505,
        "engine_type": ("data_extractor",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "extract_meta_data.py",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/spectrum_meta_data_1_0_0.zip",
                    "urn_md5": "225a49793df934ec9fe7e72822508bd5",
                    "external_url": "https://raw.githubusercontent.com/computational-ms/simepy/main/example_scripts/extract_meta_data.py",
                    "external_md5": "e54c37ad0baccab9b898025e4c06630d",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "unimod_mapper",
                    "simepy",
                ],
            },
        },
        # ^-- TODO: this does not seem to work. All tests are skipped, even if working
        #       with mzml files only
        "input_uftypes": {
            urgap.uftypes.proteomics.THERMO_RAW: {
                "min": 0,
                "max": 1,
            },
            urgap.uftypes.any.MZML: {
                "min": 0,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.RUN_META_CSV: {"min": 1, "max": 1},
            urgap.uftypes.ms.SPECTRA_META_CSV: {"min": 1, "max": 1},
            urgap.uftypes.ms.SPECTRA_NOISE_CSV: {"min": 1, "max": 1},
            urgap.uftypes.ms.INSTRUMENT_UNIT_CSV: {"min": 1, "max": 1},
        },
        "utranslation_style": "spectrum_meta_data_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize spectrum_meta_data_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for spectrum_meta_data_1_0_0 wrapper.

        Checks that only one file at a time is processed and if so, provides the file
        path to the main function of the resource to extract metadata from.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        index_dict = utrace.input_files.get_index_groups_by_uftypes()
        uftype_to_process = None
        for uftype, index_list in index_dict.items():
            if len(index_list) > 0:
                if uftype_to_process is None:
                    uftype_to_process = uftype
                else:
                    logging.warning(
                        "Meta node received multiple mass spec files, "
                        "however node can only process one at the time!"
                        f" Therefore will process {uftype_to_process} but not"
                        f" {uftype}!",
                    )

        idx_ms = index_dict[uftype_to_process][0]
        input_file = utrace.input_files[idx_ms]

        run_meta_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.RUN_META_CSV,
        )[0]
        spec_meta_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SPECTRA_META_CSV,
        )[0]
        spec_noise_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SPECTRA_NOISE_CSV,
        )[0]
        instrument_unit_output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.INSTRUMENT_UNIT_CSV,
        )[0]
        time_format = utrace.urun_dict.translations["all_params"]["time_format"][
            "translated_value"
        ]
        object_name = input_file.object_name
        lineage_root = ",".join(input_file.lineage_root_files)
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(input_file.path),
            "-ro",
            str(run_meta_output_file),
            "-so",
            str(spec_meta_output_file),
            "-sno",
            str(spec_noise_output_file),
            "-iuo",
            str(instrument_unit_output_file),
            "-tf",
            str(time_format),
            "-on",
            str(object_name),
            "-lr",
            str(lineage_root),
        ]

        return utrace
