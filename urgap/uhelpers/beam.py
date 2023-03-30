import argparse
import copy
import json
import logging
from pathlib import Path

import apache_beam as beam




    Args:

    Returns:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_json",
        dest="input_json",
        default="[{}]",
        help="input JSON file with process info.",
    )
    known_args, pipeline_args = parser.parse_known_args(argv)

        input_json = json.load(jf)

    default_config_json = input_json.get("default_pipeline_config_json", None)
    if default_config_json is not None:
        default_config_json = (
            Path(known_args.input_json) / Path(default_config_json)
        ).resolve()
            default_pipeline_args = json.load(jf)
    else:
        default_pipeline_args = {}

    manual_pipeline_args = {}
    for arg in pipeline_args:
        key_value_pair = arg.split("=")
        manual_pipeline_args[key_value_pair[0]] = None
        if len(key_value_pair) > 1:
            manual_pipeline_args[key_value_pair[0]] = key_value_pair[1]


    # Extract pipeline configuration from default configuration
    pipeline_config = default_pipeline_args.get("pipeline_configuration", {})
    # Overwrite with explicit pipeline configuration
    pipeline_config.update(input_json.get("pipeline_configuration", {}))
    # Manual overrides
    pipeline_config.update(manual_pipeline_args)

    pipeline_args = []
    for key, value in pipeline_config.items():
        if value is None:
            pipeline_args.append(key)
        else:
            pipeline_args.append(f"{key}={value}")

    for pos, _ in enumerate(pipeline_args):
        if "job_name" in _:

    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

    return pipeline_options, urd, input_json



    def __init__(

        Args:
        """
        self.kwargs = kwargs
        self.ready = False
        self.window = beam.transforms.window.GlobalWindow()
        self.unode = None
        self.urd = copy.deepcopy(urd)
        if ucredentials is not None:
            self.ucredentials = copy.deepcopy(ucredentials)
        else:
            self.ucredentials = []
        if config is not None:
            self.config = config
        else:
            self.config = {}

        if self._check_input(unode=unode, urd=urd):
            self.ready = True


        Args:

        Returns:
        """
        input_is_ok = True
            input_is_ok = False
            input_is_ok = False
            )
        return input_is_ok


        """Execute before a bundle starts."""


        Args:

        Yields:
        """
        if len(utuple) != 2:
            )
        input_group_key, elements = utuple

            for x in nested_list:
                else:
                    yield x

        if self.ready is True:

            output_ufiles = self.unode.run(
                ufiles=ufile_list,
                urun_dict=self.urd,
                **self.kwargs,
            )
            yield input_group_key, [u.as_uri() for u in output_ufiles]






    Args:

    Returns:
    """
    from apache_beam.runners.interactive.display import pipeline_graph

    s = pipeline_graph.PipelineGraph(pipeline).get_dot()
    net = Network(
        height="1500px",
        width="100%",
        directed=True,
        font_color="white",
    )
    net.use_DOT = True
    net.dot_lang = " ".join(s.split("\n"))
    net.dot_lang = net.dot_lang.replace('"', '\\"')
    net.dot_lang = net.dot_lang.replace("fontcolor=blue", "fontcolor=white")
    return net


class Concat(beam.DoFn):


        Args:

        Yields:
        """
        element_key, element_list = element
        copy_of_element_list = element_list[:]
        for side_key, side_list in side:
            if key_aware is True and side_key != element_key:
                continue
            copy_of_element_list += side_list
        yield (element_key, copy_of_element_list)


class FilterByUftype(beam.DoFn):


        Args:

        Yields:
        """
        element_key, element_list = element
        if uftypes is not None:
            if mode == "remove":
                uflist = uflist.remove_uftypes(uftypes)
            if mode == "keep":
                uflist = uflist.keep_uftypes(uftypes)
        yield (element_key, [uf.as_uri() for uf in uflist])

