"""Urgap PymzMLToIDXGZ wrapper."""

import urgap


class PymzMLToIDXGZ(urgap.unode.UNodeBase):
    """Urgap wrapper for the PymzMLToIDXGZ module.

    Pymzml allows to parse mzML data in Python based on cElementTree. See publication
    provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "PymzMLToIDXGZ",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {
                "version": "2.6.0",
                "exe_path": "MsDataConversion/PymzMLToIDXGZ/2_6_0/pymzml2idxgz.py",
            },
        ],
        "parameters_not_triggering_rerun": [],
        "engine_type": ("converter", "proteomics"),
        "engine": None,
        "input_uftypes": {
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.ms.converter.mzml.PYMZML_IDXGZ: {"min": 1, "max": 1},
        },
        "citation": """
        Kösters, M., Leufken, J., Schulze, S., Sugimoto, K., Klein, J., Zahedi, R. P., Hippler, M., Leidel, S. A., & Fufezan, C. (2018). pymzML v2.0: introducing a highly compressed and seekable gzip format.
        In J. Wren (Ed.), Bioinformatics (Vol. 34, Issue 14, pp. 2513-2514). Oxford University Press (OUP). https://doi.org/10.1093/bioinformatics/bty046
        """,
        "input_extensions": [".mzML"],
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize PymzMLToIDXGZ class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for PymzMLToIDXGZ wrapper.

        Prepares the cmd to execute with the PymzMLToIDXGZ resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        mzml_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML,
        )[0]
        idxgz_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.converter.mzml.PYMZML_IDXGZ,
        )[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            str(mzml_file),
            str(idxgz_file),
        ]

        return utrace
