"""Urgap pymzml2mgf_2_5 wrapper."""

import urgap


class pymzml2mgf_2_5(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymzml2mgf_2_5 module.

    Pymzml allows to parse mzML data in Python based on cElementTree. See publication
    provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "pymzml2mgf_2_5",
        "version": "2.5",
        "release_date": "2020-06-05",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "api_port": 42402,
        "engine_type": ("converter", "proteomics"),
        "platform_independent": True,
        "engine": {
            "platform_independent": {"arc_independent": {"exe": "pymzml2mgf.py"}},
        },
        "input_uftypes": {
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.converter.PYMZML_MGF: {"min": 1, "max": 1},
        },
        "utranslation_style": "mzml2mgf_style_1",
        "citation": """
        Kösters, M., Leufken, J., Schulze, S., Sugimoto, K., Klein, J., Zahedi, R. P., Hippler, M., Leidel, S. A., & Fufezan, C. (2018). pymzML v2.0: introducing a highly compressed and seekable gzip format.
        In J. Wren (Ed.), Bioinformatics (Vol. 34, Issue 14, pp. 2513-2514). Oxford University Press (OUP). https://doi.org/10.1093/bioinformatics/bty046
        """,
        "input_extensions": [".mzML", ".mzML.gz", ".idx.gz"],
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymzml2mgf_2_5 class."""
        super().__init__(*args, **kwargs)

    def execute(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Execute routine for pymzml2mgf_2_5 wrapper.

        Executes the main function of the pymzml2mgf_2_5 resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        kwargs = {}
        for _urgap_key, translation_dict in utrace.urun_dict.translations[
            "all_params"
        ].items():
            kwargs[translation_dict["translated_key"]] = translation_dict[
                "translated_value"
            ]

        mzml_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML,
        )[0]
        mgf_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.converter.PYMZML_MGF,
        )[0]
        _main = self.import_engine_as_python_function()
        _main(
            mzml=mzml_file,
            mgf=mgf_file,
            **kwargs,
        )
        return utrace
