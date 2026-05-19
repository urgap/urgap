"""Urgap PymzMLToMGF wrapper."""

import logging

import urgap


class PymzMLToMGF(urgap.unode.UNodeBase):
    """Urgap wrapper for the PymzMLToMGF module.

    Pymzml allows to parse mzML data in Python based on cElementTree. See publication
    provided under META_INFO["citation"] for further info.
    """

    META_INFO = {
        "name": "PymzMLToMGF",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {
                "version": "2.6.0",
                "exe_path": "MsDataConversion/pymzml_to_mgf/2_6_0/pymzml2mgf.py",
            }
        ],
        "parameters_not_triggering_rerun": [],
        "engine_type": ("converter", "proteomics"),
        "engine": None,
        "input_uftypes": {
            urgap.uftypes.ms.converter.mzml.ANY: {
                "min": 1,
                "max": 1,
            }
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.converter.PYMZML_MGF: {"min": 1, "max": 1},
        },
        "citation": """
        Kösters, M., Leufken, J., Schulze, S., Sugimoto, K., Klein, J., Zahedi, R. P., Hippler, M., Leidel, S. A., & Fufezan, C. (2018). pymzML v2.0: introducing a highly compressed and seekable gzip format.
        In J. Wren (Ed.), Bioinformatics (Vol. 34, Issue 14, pp. 2513-2514). Oxford University Press (OUP). https://doi.org/10.1093/bioinformatics/bty046
        """,
        "input_extensions": [".mzML", ".idx.gz"],
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize PymzMLToMGF class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Execute routine for PymzMLToMGF wrapper.

        Executes the main function of the PymzMLToMGF resource.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        mzml_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.ms.converter.mzml.ANY
        )[0]
        mgf_file = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.proteomics.converter.PYMZML_MGF
        )[0]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            mzml_file,
            "-o",
            mgf_file,
        ]
        for parameter_key, parameter_value in utrace.urun_dict.parameters[
            f"{self.META_INFO['unode_full_identifier']}"
        ].items():
            if parameter_value is not None:
                utrace.urun_dict.command_list.extend([parameter_key, parameter_value])

        return utrace
