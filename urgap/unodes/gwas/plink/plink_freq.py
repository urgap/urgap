"""Urgap PlinkFreq wrapper for allele frequency calculation."""

from pathlib import Path

import urgap


class PlinkFreq(urgap.unode.UNodeBase):
    """Urgap wrapper for PLINK2 allele frequency calculation."""

    META_INFO = {
        "name": "PlinkFreq",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "2.0.0a2.post3", "exe_path": "$plink2"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.genomics.plink.BED: {"min": 1, "max": 1},
            urgap.uftypes.genomics.plink.BIM: {"min": 1, "max": 1},
            urgap.uftypes.genomics.plink.FAM: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.genomics.plink.FREQ: {"min": 1, "max": 1},
            urgap.uftypes.genomics.plink.LOG: {"min": 1, "max": 1},
        },
        "engine": None,
        "engine_type": ("gwas",),
        "citation": """TBA""",
    }

    def __init__(self) -> None:
        """Initialize PlinkFreq class."""
        super().__init__()

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for PlinkFreq wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object.
        """
        bed_path = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.genomics.plink.BED,
        )[0]

        # PLINK uses the prefix without extension
        plink_prefix = bed_path.with_suffix("")

        # Output prefix on scratch disk
        output_prefix = urgap.scratch_disk_base / "plink_freq_output"

        utrace.urun_dict.command_list = [
            str(self.exe_path),
            "--bfile",
            str(plink_prefix),
            "--freq",
            "--out",
            str(output_prefix),
        ]

        # Add additional parameters
        for key, value in utrace.urun_dict.parameters.items():
            if key.startswith("--"):
                if value is True:
                    utrace.urun_dict.command_list.append(key)
                elif value is not False and value is not None:
                    utrace.urun_dict.command_list.extend([key, str(value)])

        utrace.urun_dict["_plink_output_prefix"] = str(output_prefix)

        return utrace

    def execute(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Execute routine for PlinkFreq wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object.
        """
        super().execute(utrace)
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for PlinkFreq wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object.
        """
        output_prefix = Path(utrace.urun_dict["_plink_output_prefix"])

        freq_output = output_prefix.with_suffix(".afreq")
        if freq_output.exists():
            freq_ufile_path = utrace.output_files.get_path_objects_by_uftype(
                urgap.uftypes.genomics.plink.FREQ,
            )[0]
            freq_ufile_path.write_bytes(freq_output.read_bytes())

        log_output = output_prefix.with_suffix(".log")
        if log_output.exists():
            log_ufile_path = utrace.output_files.get_path_objects_by_uftype(
                urgap.uftypes.genomics.plink.LOG,
            )[0]
            log_ufile_path.write_bytes(log_output.read_bytes())

        return utrace
