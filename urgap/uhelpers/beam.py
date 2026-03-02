"""UHelper.beam module of urgap."""

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

import urgap

P = ParamSpec("P")
logger = logging.getLogger(__name__)


def parse_inputs(
    argv: list,
    save_main_session: bool,
) -> tuple[PipelineOptions, urgap.URunDict, dict]:
    """Parse command line inputs and return pipeline options, URunDict, and input json.

    Args:
        argv: Command line arguments.
        save_main_session: Whether to save main session for Beam (required for some runners).

    Returns:
        Pipeline options, Urgap URunDict, and the input JSON dict.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_json",
        dest="input_json",
        default="[{}]",
        help="input JSON file with process info.",
    )
    known_args, pipeline_args = parser.parse_known_args(argv)

    with known_args.input_json.open() as jf:
        input_json = json.load(jf)

    default_config_json = input_json.get("default_pipeline_config_json", None)
    if default_config_json is not None:
        default_config_json = (
            Path(known_args.input_json) / Path(default_config_json)
        ).resolve()
        with default_config_json.open() as jf:
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
    urd = urgap.URunDict(input_json.get("urun_dict", {}))

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


class UrgapNodeExecutor(beam.DoFn):
    """Executes an Urgap node as a Beam DoFn."""

    def __init__(
        self,
        unode: str = "None",
        urd: urgap.URunDict | None = None,
        ucredentials: list | None = None,
        config: dict | None = None,
        **kwargs: P.kwargs,
    ) -> None:
        """Initialize wrapper for Urgap Nodes as Apache Beam DoFn.

        Args:
            unode: Urgap UNode name.
            urd: Urgap URunDict.
            config: Temporary Urgap config (does not overwrite main config).
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
            self.unode = urgap.init_node(unode)
            msg = f"Setting up urgap unode {self.unode} with {urd.parameters}"
            logger.debug(msg)

    def _check_input(
        self,
        unode: str | None = None,
        urd: urgap.URunDict | None = None,
    ) -> bool:
        """Check validity of unode and urd input.

        Args:
            unode: Urgap UNode name.
            urd: Urgap URunDict.

        Returns:
            True if input is valid, else False.
        """
        input_is_ok = True
        if not isinstance(urd, urgap.URunDict):
            input_is_ok = False
            msg = f"{urd} is not a urgap URunDict!"
            logger.warning(msg)
        if unode not in urgap.instances.unode_manager.wrapper_lookup:
            input_is_ok = False
            msg = (
                f"{unode} is not a urgap node. "
                f"Available nodes are {list(urgap.instances.unode_manager.wrapper_lookup.keys())}"
            )
            logger.warning(msg)
        return input_is_ok

    def setup(self) -> None:
        """Set up DoFn (e.g., open DB connections)."""

    def start_bundle(self) -> None:
        """Execute before a bundle starts."""

    def process(self, utuple: tuple) -> list[tuple]:
        """Run Urgap node for the given tuple input.

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
            logger.warning(msg)
        input_group_key, elements = utuple

        def _unpack_list(nested_list: list) -> Generator:
            for x in nested_list:
                if isinstance(x, (tuple, list)):
                    yield from _unpack_list(x)
                else:
                    yield x

        if self.ready is True:
            urgap.config.update(self.config)
            urgap.instances.ucredential_manager.add_credentials(self.ucredentials)
            ufile_list = urgap.UFileList.from_uri_list(list(_unpack_list(elements)))

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
    """Concat PColl to another PColl, Urgap style."""

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
        uflist = urgap.UFileList.from_uri_list(element_list)
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
        uf_list = urgap.UFileList.from_uri_list(element_list)
        renamed_uf_list = uf_list.simplify_names(
            source_object_names=source_object_names,
            prefix=prefix,
            suffix=suffix,
        )
        for uf in renamed_uf_list:
            yield (element_key, [uf.as_uri()])
