"""Urgap extract_gatingxml_stats_1_0_0 wrapper."""

import logging

import urgap


class extract_gatingxml_stats_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the extract_gatingxml_stats_1_0_0 resource.

    Used to extract statistics from flowJo gated files using a WSP FlowJo files.
    """

    META_INFO = {
        "name": "extract_gatingxml_stats_1_0_0",
        "version": "1.0.0",
        "release_date": "03.08.2023",
        "api_port": 42109,
        "engine_type": (
            "flow_cytometry",
            "secondary_analysis",
            "stats",
        ),
        "wrapper_version": {
            "major": 1,
            "minor": 0,
            "patch": 0,
        },
        "platform_independent": True,
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "extract_gatingxml_stats_1_0_0.py",
                },
            },
        },
        "requires": {
            "other_uftypes": {
                "python_packages": [
                    "flowkit",
                    "unimod_mapper",
                ],
            },
        },
        "utranslation_style": "extract_flowjo_stats_style_1",
        "input_uftypes": {
            urgap.uftypes.flow_cytometry.FCS: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.gating_strategy.ANY: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.flow_cytometry.stats.FREQS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.stats.STATS_CSV: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.flow_cytometry.stats.GATING_TREE: {
                "min": 1,
                "max": 1,
            },
        },
        "citation": "Urgap team (2021)",
    }

    def __init__(self, *args: str, **kwargs: str):
        """Initialize extract_gatingxml_stats_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for extract_gatingxml_stats_1_0_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        input_groups = utrace.input_files.get_path_object_groups_by_uftypes()
        output_groups = utrace.output_files.get_path_object_groups_by_uftypes()
        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-f",
            str(input_groups[urgap.uftypes.flow_cytometry.FCS][0]),
            "-os",
            str(output_groups[urgap.uftypes.flow_cytometry.stats.STATS_CSV][0]),
            "-of",
            str(output_groups[urgap.uftypes.flow_cytometry.stats.FREQS_CSV][0]),
            "-og",
            str(output_groups[urgap.uftypes.flow_cytometry.stats.GATING_TREE][0]),
        ]

        if urgap.uftypes.flow_cytometry.gating_strategy.CYTOBANK_XML in input_groups:
            utrace.urun_dict.command_list += [
                "-cb",
                input_groups[urgap.uftypes.flow_cytometry.gating_strategy.CYTOBANK_XML][
                    0
                ],
            ]
        elif urgap.uftypes.flow_cytometry.gating_strategy.FLOWJO_WSP in input_groups:
            utrace.urun_dict.command_list += [
                "-w",
                input_groups[urgap.uftypes.flow_cytometry.gating_strategy.FLOWJO_WSP][
                    0
                ],
            ]
        else:
            logging.warning(
                "Cannot process gating XML. Only FLowJo and Cytobank are currently supported",
            )

        return utrace
