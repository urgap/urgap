"""Urgap generate_experimental_design_px_1_0_0 wrapper."""

import urgap

from urgap.wrappers.io.experimental_design_generator.generate_experimental_design_1_0_0 import (
    GenerateExperimentalDesign_1_0_0 as generate_experimental_design_base,
)


class GenerateExperimentalDesignPX_1_0_0(generate_experimental_design_base):
    """Urgap wrapper for the generate_experimental_design_px_1_0_0 resource.

    Based on a user input metadata, generates an experimental design relevant for the
    pipeline execution.
    """

    META_INFO = {
        "name": "generate_experimental_design_px_1_0_0",
        "version": "1.0.0",
        "release_date": "15.03.2023",
        "api_port": 42204,
        "engine_type": ("io",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "platform_independent": True,
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "generate_experimental_design_1_0_0.py",
                },
            },
        },
        "exe_path": "generate_experimental_design_1_0_0/generate_experimental_design_1_0_0.py",
        "utranslation_style": "exp_design_generator_style_1",
        "input_uftypes": {
            urgap.uftypes.exp_design.input.PX_METADATA_JSON: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.any.MZML: {
                "min": 0,
                "max": -1,
            },
            urgap.uftypes.any.RAW: {
                "min": 0,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.exp_design.output.PX_METADATA_CSV: {
                "min": 1,
                "max": 1,
            },
        },
        "citation": "Urgap team (2023)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize generate_experimental_design_px_1_0_0 class."""
        super().__init__(*args, **kwargs)
