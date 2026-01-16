"""Urgap generate_experimental_design_1_0_0 wrapper."""

import json
import logging

import urgap


class GenerateExperimentalDesign_1_0_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the generate_experimental_design_1_0_0 resource.

    Based on a user input metadata, generates an experimental design relevant for the
    pipeline execution.
    """

    META_INFO = {
        "name": "generate_experimental_design_1_0_0",
        "version": "1.0.0",
        "release_date": "15.03.2023",
        "api_port": 42202,
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
        "utranslation_style": "exp_design_generator_style_1",
        "input_uftypes": {
            urgap.uftypes.exp_design.input.ANY: {
                "min": 1,
                "max": 1,
            },
            urgap.uftypes.any.MZML: {
                "min": 0,
                "max": -1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.exp_design.output.ANY: {
                "min": 1,
                "max": 1,
            },
        },
        "citation": "Urgap team (2023)",
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize generate_experimental_design_1_0_0 class."""
        super().__init__(*args, **kwargs)

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for generate_experimental_design_1_0_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        logging.info("[ -ENGINE- ] Defining the correct uftype to be processed..")

        index_dict = utrace.input_files.get_index_groups_by_uftypes()

        process_uftypes_lookup_list = [
            set[1]
            for set in urgap.instances.utree_querier.get_leafs_from_node(
                node=urgap.uftypes.exp_design.input.ANY,
            )
        ]

        uftype_to_process_list = []
        uftype_to_map_list = []
        for key in index_dict:
            if key in process_uftypes_lookup_list:
                uftype_to_process_list.append(key)
            else:
                uftype_to_map_list.append(key)

        # Define the lineage root lookup list
        lookup_files = []
        for uftype in uftype_to_map_list:
            idx = utrace.input_files.get_indices_by_uftype(uftype)
            ufiles = [utrace.input_files[id] for id in idx]
            lookup_files.extend(ufiles)

        object_names_mapping = {}
        for file in lookup_files:
            parents = file.parents
            if len(parents) == 0:
                parents = [file.object_name]
            object_names_mapping[file.object_name] = parents

        parents_json_path = utrace.output_files[0].path.parent / "parents.json"
        with open(parents_json_path, "w") as file:
            json.dump(object_names_mapping, file)

        # TODO: should there be a check that the resource does not even start if the
        #  object_names list is empty? Or should this be checked in the resource?

        mapping_column = utrace.urun_dict.translations["all_params"]["mapping_column"][
            "translated_value"
        ]

        utrace.urun_dict.command_list = [
            "python",
            str(self.exe_path),
            "-i",
            str(
                utrace.input_files.get_path_objects_by_uftype(
                    uftype_to_process_list[0],
                )[0],
            ),
            "-o",
            str(utrace.output_files[0].path),
            "-m",
            uftype_to_process_list[0],
            "-par",
            str(parents_json_path),
            "-mc",
            mapping_column,
        ]

        return utrace
