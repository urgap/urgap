"""Urgap generate_target_decoy_fasta_2_0_0 wrapper."""

import urgap


class generate_target_decoy_fasta_2_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the generate_target_decoy_fasta_2_0_0 resource.

    Allows to create a target decoy database from one (or more) fasta files.
    """

    META_INFO = {
        "name": "generate_target_decoy_fasta_2_0_0",
        "version": "2.0.0",
        "release_date": "5.4.2022",
        "wrapper_version": {"major": 2, "minor": 0, "patch": 0},
        "api_port": 42707,
        "engine_type": ("proteomics",),
        "platform_independent": True,  # !
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "generate_target_decoy_fasta_2_0_0.py",
                    # "zip_md5": "<>",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "pyahocorasick",
                    "unimod_mapper",
                ],
            },
        },
        "input_uftypes": {
            urgap.uftypes.proteomics.FASTA: {
                "min": 1,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.proteomics.FASTA: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.ms.IMMUTABLE_PEPTIDES: {
                "min": 1,
                "max": 1,
            },
        },
        "utranslation_style": "generate_target_decoy_style_1",
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize generate_target_decoy_fasta_2_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for generate_target_decoy_fasta_2_0_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "--output",
            str(
                utrace.output_files.get_path_objects_by_uftype(
                    urgap.uftypes.proteomics.FASTA,
                )[0],
            ),
            "--immutable_file",
            str(
                utrace.output_files.get_path_objects_by_uftype(
                    urgap.uftypes.ms.IMMUTABLE_PEPTIDES,
                )[0],
            ),
            "--enzyme_pattern",
            utrace.urun_dict.translations["all_params"]["enzyme"]["translated_value"],
            "--decoy_tag",
            utrace.urun_dict.translations["all_params"]["decoy_tag"][
                "translated_value"
            ],
            "--seed",
            utrace.urun_dict.translations["all_params"]["random_seed"][
                "translated_value"
            ],
            "--mode",
            utrace.urun_dict.translations["all_params"]["decoy_generation_mode"][
                "translated_value"
            ],
            "--input",
        ]
        for ufile in utrace.input_files:
            utrace.urun_dict.command_list.append(str(ufile.path))
        return utrace
