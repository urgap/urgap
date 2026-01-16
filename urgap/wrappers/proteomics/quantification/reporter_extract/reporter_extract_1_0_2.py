"""Urgap reporter s2i correct  wrapper."""

import urgap


class reporter_extract_1_0_2(urgap.unode.UNodeBase):
    """reporter_extract_1_0_2 Urgap Node."""

    META_INFO = {
        "name": "reporter_extract_1_0_2",
        "version": "1.0.2",
        "release_date": "22.02.2022",
        "api_port": 42728,
        "engine_type": ("quantification", "proteomics"),
        "platform_independent": True,  # The executable for platform independent is expected to be under
        # $URGAP_HOME/resources/platform_independent/arc_independent/frag_ion_manip_1_0_0/
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "reporter_extract_1_0_2.py",
                    # "zip_md5": "<>",
                },
            },
        },
        "wrapper_version": {
            "major": 1,
            "minor": 0,
            "patch": 0,
        },
        "input_uftypes": {
            urgap.uftypes.ms.SPECTRA_META_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.SCANS_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.quantification.reporter_ions.REPORTER_IONS: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "reporter_extract_style_1",
        "citation": "Urgap team (2022)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize reporter_extract_1_0_2 class."""
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
        msmsions_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SCANS_CSV,
        )[0]
        spec_meta_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.SPECTRA_META_CSV,
        )[0]

        output_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.quantification.reporter_ions.REPORTER_IONS,
        )[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "--msms_ions",
            str(msmsions_file),
            "--scan_meta",
            str(spec_meta_file),
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
        """Postflight.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        lineage_roots = utrace.input_files[0].lineage_root_files
        urgap.ucore.set_column_value(
            utrace.output_files[0].path,
            "filename",
            lineage_roots[0],
        )
        return utrace
