
import argparse
import copy
import json
import logging

from collections.abc import Generator
from pathlib import Path
from typing import ParamSpec

import apache_beam as beam

from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions
from pyvis.network import Network


P = ParamSpec("P")


def parse_inputs(
    argv: list,
    save_main_session: bool,
    """Parse command line inputs and return pipeline options, URunDict, and input json.

    Args:
        argv: Command line arguments.
        save_main_session: Whether to save main session for Beam (required for some runners).

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

    if "credentials_lookup" not in input_json:
        input_json["credentials_lookup"] = None

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
            pipeline_args[pos] += f"-{urd.wid.replace('_', '-')}"

    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

    return pipeline_options, urd, input_json


def flatten_to_list(pcol_input: list) -> list:
    """Flatten a list of keyed UFile groups into a single grouped list.

    Args:
        pcol_input: List of tuples (key, list_of_ufiles).

    Returns:
        List: [group_key, combined_ufiles]
    """
    ufiles = []
    for i in pcol_input:
        ufiles += i[1]
    return ["GroupKey", ufiles]



    def __init__(
        self,
        unode: str = "None",
        ucredentials: list | None = None,
        config: dict | None = None,
        **kwargs: P.kwargs,
    ) -> None:

        Args:
            ucredentials: List of credentials to add before execution.
            kwargs: Extra kwargs to be passed to unode.run.
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

    def _check_input(
        self,
        unode: str | None = None,
    ) -> bool:
        """Check validity of unode and urd input.

        Args:

        Returns:
            True if input is valid, else False.
        """
        input_is_ok = True
            input_is_ok = False
            input_is_ok = False
            msg = (
            )
        return input_is_ok

    def setup(self) -> None:
        """Set up DoFn (e.g., open DB connections)."""

    def start_bundle(self) -> None:
        """Execute before a bundle starts."""

    def process(self, utuple: tuple) -> list[tuple]:

        Args:
            utuple: (group_key, ufile_uris) as a tuple, where ufile_uris can be nested.

        Yields:
            Tuple: (input_group_key, list of output UFile .as_uri() strings).
        """
        if len(utuple) != 2:
            msg = (
                f"Cannot process {utuple} as input format must be a tuple "
                "in the form of (groupByKey, list of ufile.as_uri strings)"
            )
        input_group_key, elements = utuple

        def _unpack_list(nested_list: list) -> Generator:
            for x in nested_list:
                if isinstance(x, (tuple, list)):
                    yield from _unpack_list(x)
                else:
                    yield x

        if self.ready is True:

            output_ufiles = self.unode.run(
                ufiles=ufile_list,
                urun_dict=self.urd,
                **self.kwargs,
            )
            yield input_group_key, [u.as_uri() for u in output_ufiles]

    def finish_bundle(self) -> None:
        """Execute after a bundle has finished."""

    def teardown(self) -> None:
        """Teardown DoFn (e.g., close DB connection)."""


def generate_pyvis_network(pipeline: beam) -> Network:
    """Generate pyvis Network visualization from a Beam pipeline.

    Note:
        Requires interactive environment (ipython/jupyter).

    Args:
        pipeline: Apache Beam pipeline.

    Returns:
        pyvis.network.Network object.
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

    def process(
        self,
        element: tuple,
        side: list[tuple] | None = None,
        key_aware: bool = False,
    ) -> tuple:
        """Concatenate side list to element list, optionally requiring keys to match.

        Args:
            element: Tuple (element_key, element_list).
            side: List of tuples (side_key, side_list) to concat to element_list.
            key_aware: If True, only concat side_list if side_key matches element_key.

        Yields:
            Tuple of (element_key, concatenated_list).
        """
        element_key, element_list = element
        copy_of_element_list = element_list[:]
        for side_key, side_list in side:
            if key_aware is True and side_key != element_key:
                continue
            copy_of_element_list += side_list
        yield (element_key, copy_of_element_list)


class FilterByUftype(beam.DoFn):
    """Filter files from a PColl by the uftype flag."""

    def process(
        self,
        element: tuple,
        uftypes: list | None = None,
        mode: str = "remove",
    ) -> tuple:
        """Filter files from PColl by uftype.

        Args:
            element: Tuple (element_key, element_list).
            uftypes: List of uftypes to filter.
            mode: "remove" or "keep" those uftypes.

        Yields:
            Tuple of (element_key, filtered list).
        """
        element_key, element_list = element
        if uftypes is not None:
            if mode == "remove":
                uflist = uflist.remove_uftypes(uftypes)
            if mode == "keep":
                uflist = uflist.keep_uftypes(uftypes)
        yield (element_key, [uf.as_uri() for uf in uflist])


class OutputRenamer(beam.DoFn):
    """Copy and rename output UFiles to user-friendly specifications."""

    def process(
        self,
        element: tuple | None = None,
        source_pcol: tuple | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
    ) -> tuple:
        """Copy and rename input UFiles.

        Files are renamed so that: <working_dir>/<prefix><source_file_stem><suffix>
        where source_file_stem is the file stem of the file in the source_pcol that is
        also in the element's parents.

        Args:
            element: Tuple (element_key, list_of_ufile_uris).
            source_pcol: Tuple with source files for mapping names.
            prefix: String to prepend to new names.
            suffix: String to append to new names.

        Yields:
            Tuple (element_key, list of renamed UFile .as_uri() strings).
        """
        element_key, element_list = element
        source_object_names = set()
        for _, source_files in source_pcol:
            for source_file in source_files:
                source_object_names.add(source_file.split("#")[-1])
        renamed_uf_list = uf_list.simplify_names(
        )
        for uf in renamed_uf_list:
            yield (element_key, [uf.as_uri()])