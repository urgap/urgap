"""Urgap pymzml2idxgz_2_5_2 wrapper."""

import urgap


class pymzml2idxgz_2_5_2(urgap.unode.UNodeBase):
    """Urgap wrapper for the pymzml2idxgz_2_5_2 module.

    Pymzml allows to parse mzML data in Python based on cElementTree. See publication
    provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "pymzml2idxgz_2_5_2",
        "version": "2.5.2",
        "release_date": "2022-09-08",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "api_port": 42401,
        "engine_type": ("converter", "proteomics"),
        "platform_independent": True,
        "engine": {
            "platform_independent": {"arc_independent": {"exe": "pymzml2idxgz.py"}},
        },
        "input_uftypes": {
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.converter.PYMZML_IDXGZ: {"min": 1, "max": 1},
        },
        "utranslation_style": "mzml2idxgz_style_1",
        "citation": """
        Kösters, M., Leufken, J., Schulze, S., Sugimoto, K., Klein, J., Zahedi, R. P., Hippler, M., Leidel, S. A., & Fufezan, C. (2018). pymzML v2.0: introducing a highly compressed and seekable gzip format.
        In J. Wren (Ed.), Bioinformatics (Vol. 34, Issue 14, pp. 2513-2514). Oxford University Press (OUP). https://doi.org/10.1093/bioinformatics/bty046
        """,
        "input_extensions": [".mzML"],
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize pymzml2idxgz_2_5_2 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for pymzml2idxgz_2_5_2 wrapper.

        Prepares the cmd to execute with the pymzml2idxgz_2_5_2 resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        mzml_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML,
        )[0]
        idxgz_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.converter.PYMZML_IDXGZ,
        )[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            str(mzml_file),
            str(idxgz_file),
        ]

        return utrace
