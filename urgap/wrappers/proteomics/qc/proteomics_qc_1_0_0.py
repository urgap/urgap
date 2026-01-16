"""Urgap proteomics_qc_1_0_0 wrapper."""

import urgap


class proteomics_qc_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the proteomics_qc_1_0_0 resource.

    This wrapper calls the main resource to compute proteomics qc metrics
    on pyProtista output files.
    """

    META_INFO = {
        "name": "proteomics_qc_1_0_0",
        "version": "1.0.0",
        "release_date": "31.08.2022",
        "api_port": 42723,
        "engine_type": ("converter", "proteomics"),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "proteomics_qc_1_0_0.py",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "chemical_composition",
                    "unimod_mapper",
                ],
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.converter.PYIOHAT_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.proteomics.MODS_XML: {"min": 0, "max": -1},
            urgap.uftypes.any.MZML: {"min": 1, "max": -1},
            urgap.uftypes.proteomics.qc.OFFSET_CSV: {"min": 0, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.any.CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "proteomics_qc_style_1",
        "citation": "Urgap team (2022)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize proteomics_qc_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for proteomics_qc_1_0_0 wrapper.

        During preflight,
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        offset_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.qc.OFFSET_CSV,
        )
        offset_files = None if len(offset_files) == 0 else offset_files[0]
        pyiohat_csv_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.converter.PYIOHAT_CSV,
        )[0]
        mzmls = utrace.input_files.get_path_objects_by_uftype(urgap.uftypes.any.MZML)
        output_file = utrace.output_files[0].path
        modification_xmls = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.MODS_XML,
        )
        matching_tolerance_in_ppm = utrace.urun_dict.translations["all_params"][
            "match_mass_tolerance"
        ]["translated_value"]
        n_cpus = utrace.urun_dict.translations["all_params"]["cpus"]["translated_value"]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(pyiohat_csv_file),
            "-o",
            str(output_file),
            "-t",
            str(matching_tolerance_in_ppm),
            "-n",
            str(n_cpus),
            "--offset",
            str(offset_files),
        ]
        for m in mzmls:
            utrace.urun_dict.command_list.append("-m")
            utrace.urun_dict.command_list.append(str(m))
        for x in modification_xmls:
            utrace.urun_dict.command_list.append("-x")
            utrace.urun_dict.command_list.append(str(x))
        return utrace
