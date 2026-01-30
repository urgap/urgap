"""Unode class.

This module defines the UnodeBase class, which is inherited by wrappers.
"""

from __future__ import annotations

import copy
import itertools
import json
import logging
import os
import platform
import shutil
import stat
import subprocess
import sys
import time

from collections.abc import Sequence
from pathlib import Path
from typing import Any, ParamSpec

import requests

try:
    from opentelemetry import trace as _ot
    from opentelemetry.trace import SpanKind, StatusCode

    _OPENTELEMETRY_AVAILABLE = True
except ImportError:
    _ot = None
    SpanKind = None
    StatusCode = None
    _OPENTELEMETRY_AVAILABLE = False

import urgap

from urgap.utelemetry import utl_trace

P = ParamSpec("P")
logger = logging.getLogger(__name__)


class UNodeBase:
    """Base class for urgap UNodes."""

    def __init__(self) -> None:
        """Initialize the UNodeBase instance."""
        self._exe_path = None
        self.status = None
        self.tmp_files = []
        self.utrace_history = []
        self.latest_exe_paths = None

    @property
    def exe_path(self) -> os.PathLike:
        """Get the path to the executable resource for this node.

        Returns:
            Path to the executable file.
        """
        if self._exe_path is None:
            self._exe_path = self.construct_exe_path()
        return self._exe_path

    @property
    def is_available(self) -> bool:
        """Check whether the resource path exists and is a file.

        Returns:
            True if the resource path exists and is a file, otherwise False.
        """
        return self.resource_is_available

    @property
    def resource_is_available(self) -> bool:
        """Check whether the resource is available.

        Note:
            This property does not guarantee that all required 3rd party installations
            are available. Use self.has_all_required_installations() for a complete check.

        Returns:
            True if the resource is available.
        """
        return urgap.instances.unode_manager.node_availability_lookup[
            self.META_INFO["unode_full_identifier"]
        ]["resource_available"]

    @property
    def requires_3rd_party_installation(self) -> bool:
        """Check whether this node requires 3rd party installations.

        Returns:
            True if 3rd party tools are required, otherwise False.
        """
        return urgap.instances.unode_manager.node_availability_lookup[
            self.META_INFO["unode_full_identifier"]
        ]["has_3rd_party_requirements"]

    def run_node_as_mcp_tool(
        self,
        ufiles: list,
        tool_parameter: dict,
        force: bool = False,
        output_urgap_storage_base_uri: str | None = None,
        latest_exe_path: str | None = None,
        workflow_id: str | None = None,
    ) -> list:
        """Run UNode via mcp tools.

        Args:
            ufiles (list of uri strings): List of urgap uri strings
            tool_parameter (dict): Parameters that are added to the
                command line for tools execution.
            output_urgap_storage_base_uri (str | None, optional):
                a urgap_storage_base_uri can be used to defines where the output files
                of the run is uploaded to. Defaults to None.
            force (bool, optional): Defines if re-run logic is checked. Defaults to False.
            latest_exe_path (str | None, optional): path to the executable. Defaults to None.
            workflow_id (str | None, optional): workflow ID. Defaults to None.

        Returns:
            list: list of uri strings
        """
        _unused_kargs_as_sometimes_to_complex_for_llm = [
            "wid (str | None, optional): workflow ID. Defaults to None.",
            "additional_filters: dict | None = None,",
            "dry_run: bool = False,",
            "override_folder_creation: bool = False,",
            "prefix: str | None = None,",
            "run_folder_name: str | None = None,",
            "skip_data_versioning: bool = False,",
            "record_skipped_runs: str | bool = False,",
            "skip_pre_checks: bool = False,",
            "remove_temporary_files: str | bool = False,",
            "retain_uftypes: str | bool = workflow ID,",
            "file_io_timeout: int | None = None,",
            "remote_url: str | None = None,",
            "remote_execution_timeout: int = 7200,",
        ]
        urun_dict = urgap.URunDict(
            {
                "parameters": {
                    self.META_INFO["unode_full_identifier"]: tool_parameter,
                },
                "unode_parameters": {
                    "storage_base_uri": output_urgap_storage_base_uri,
                    "latest_exe_paths": {
                        "force": force,
                        self.META_INFO["unode_full_identifier"]: latest_exe_path,
                    },
                },
            },
        )
        if workflow_id is not None:
            urun_dict["wid"] = workflow_id
        ufile_list = self.run(ufiles, urun_dict)
        uri_list = ufile_list.as_uri_list()
        if isinstance(uri_list, str):
            uri_list = [uri_list]
        return uri_list

    @staticmethod
    def _extract_attrs(a: Sequence[Any], kw: dict[str, Any]) -> dict[str, Any]:
        if len(a) > 2 and a[2] is not None:
            wid_value = a[2].wid
        elif kw.get("urun_dict"):
            wid_value = kw["urun_dict"].wid
        else:
            wid_value = None

        return {
            "wid": wid_value,
            "unode_full_identifier": a[0].META_INFO["unode_full_identifier"],
        }

    @utl_trace(
        span_name="unode.run",
        attributes={"component": "unode"},
        attrs_from=_extract_attrs,
    )
    def run(
        self,
        ufiles: urgap.UFileList | None = None,
        urun_dict: urgap.URunDict | None = None,
        **kwargs: P.kwargs,
    ) -> urgap.UFileList:
        """Run the Urgap node.

        Args:
            ufiles: List of UFile objects or a single UFile to process.
            urun_dict: URunDict with parameters for the node.
            kwargs: Additional unode_parameters to manually supply or override.

        Returns:
            The resulting output UFileList after execution.
        """
        if isinstance(urun_dict, urgap.URunDict) is False:
            msg = "UNode.run() function requires URunDict."
            logger.error(msg)
            raise TypeError(msg)
        urun_dict = copy.deepcopy(urun_dict)

        if (
            self.META_INFO["unode_version"] is not None
            and self.META_INFO["unode_version"] == "latest"
        ):
            self.latest_exe_paths = urun_dict.unode_parameters["latest_exe_paths"].get(
                f"{self.META_INFO['unode_full_identifier']}",
                None,
            )

        if urun_dict.unode_parameters["skip_pre_checks"] is False:
            self._pre_checks()

        self.tmp_files = []
        if len(kwargs.keys()) != 0:
            logger.warning("Manually overwriting UNode parameters.")
            urun_dict.unode_parameters.update(kwargs)

        if urun_dict["unode_parameters"]["remote_url"] is None:
            logger.debug("Running locally")
            output_files = self._run_locally(ufiles=ufiles, urun_dict=urun_dict)
        else:
            output_files = self._run_remotely(ufiles=ufiles, urun_dict=urun_dict)

        return output_files

    @staticmethod
    def _extract_remote_attrs(a: Sequence[Any], kw: dict[str, Any]) -> dict[str, Any]:
        if kw.get("urun_dict"):
            wid_value = kw["urun_dict"].wid
        elif len(a) > 2 and a[2] is not None:
            wid_value = a[2].wid
        else:
            wid_value = None

        return {
            "wid": wid_value,
            "unode_full_identifier": a[0].META_INFO["unode_full_identifier"],
            "function.role": "client",
        }

    @utl_trace(
        span_name="unode.run_remote",
        attributes={"component": "unode"},
        attrs_from=_extract_remote_attrs,
    )
    def _run_remotely(
        self,
        ufiles: urgap.UFileList | list[urgap.UFile] | list[str] | None = None,
        urun_dict: urgap.URunDict | None = None,
    ) -> urgap.UFileList:
        """Run the node remotely via HTTP POST to the remote server.

        Args:
            ufiles: List of UFile objects or their UUris to process.
            urun_dict: URunDict containing execution parameters.

        Returns:
            UFileList resulting from remote execution.
        """
        if isinstance(ufiles, urgap.UFileList):
            ufiles_list: list[str] = [uf.as_uri() for uf in ufiles]
        elif isinstance(ufiles, list):
            ufiles_list = [
                uf.as_uri() if isinstance(uf, urgap.UFile) else uf for uf in ufiles
            ]
        else:
            ufiles_list = []

        port = urgap.instances.unode_manager.unode_port_mapping[
            self.META_INFO["unode_full_identifier"]
        ]
        remote_url = f"{urun_dict['unode_parameters']['remote_url']}:{port}/v1/run"

        urun_dict["is_remote_run"] = True

        span = _ot.get_current_span() if _OPENTELEMETRY_AVAILABLE else None
        span_rec = span is not None and span.is_recording()
        if span_rec:
            span.set_attribute("http.method", "POST")
            span.set_attribute("http.url", remote_url)
            span.set_attribute("span.kind", str(SpanKind.CLIENT))
            span.set_attribute("ufiles.count", len(ufiles_list))

        payload = json.dumps(
            {
                "urun_dict": dict(urun_dict.items()),
                "ufiles": ufiles_list,
                "config": urgap.config,
                "ucredentials": list(
                    urgap.instances.ucredential_manager.ingested_credentials.values(),
                ),
            },
            indent=2,
            allow_nan=True,
            sort_keys=True,
            cls=urgap.uconvert.JSONEncoder,
        )

        try:
            response = requests.post(
                remote_url,
                json=payload,
                timeout=urun_dict["unode_parameters"]["remote_execution_timeout"],
            )
        except Exception as e:
            if span_rec:
                span.set_attribute("exception.type", type(e).__name__)
                span.set_attribute("exception.message", str(e))
            msg = f"Remote execution failed with error: {e}"
            logger.exception(msg)
            raise requests.HTTPError(msg) from e

        if span_rec:
            span.set_attribute("http.status_code", int(response.status_code))
            span.set_status(StatusCode.OK if response.ok else StatusCode.ERROR)

        data = response.json()
        if not response.ok:
            msg = f"Remote error: {data.get('error')}\n\nTraceback:\n{data.get('traceback')}"
            raise RuntimeError(msg)

        return urgap.UFileList.from_uri_list(data)

    @utl_trace(
        span_name="unode.run_local",
        attributes={"component": "unode"},
        attrs_from=lambda a, kw: {
            "unode_full_identifier": a[0].META_INFO["unode_full_identifier"],
            "wid": kw["urun_dict"].wid
            if "urun_dict" in kw and kw["urun_dict"] is not None
            else None,
            "span.kind": str(SpanKind.INTERNAL) if SpanKind is not None else "INTERNAL",
        },
    )
    def _run_locally(
        self,
        ufiles: urgap.UFileList | None = None,
        urun_dict: urgap.URunDict | None = None,
    ) -> urgap.UFileList:
        """Run the node locally.

        Args:
            ufiles: List of UFile objects or their UUris to process.
            urun_dict: URunDict containing execution parameters.

        Returns:
            UFileList with results of the local execution.
        """
        if ufiles is None:
            ufiles = urgap.UFileList([])
        elif isinstance(ufiles, urgap.UFileList) is False:
            if all(isinstance(file, str) for file in ufiles):
                ufiles = urgap.UFileList.from_uri_list(ufiles)
            else:
                ufiles = urgap.UFileList(ufiles)

        urgap.scratch_disk = urgap.scratch_disk_base / urun_dict.wid
        ufiles = ufiles.create_flat_and_non_redundant_list()

        ut = urgap.UTrace(
            urun_dict=urun_dict,
            input_files=ufiles,
            unode_meta=self.META_INFO,
            unode_version=self.META_INFO["unode_version"],
        )
        ut.input_files = ut.filter_input_files(ut.input_files)

        span = _ot.get_current_span() if _OPENTELEMETRY_AVAILABLE else None
        if span is not None and span.is_recording():
            span.set_attribute("utrace.output_files_stem", ut.output_files_stem)
            span.set_attribute(
                "is_remote_run",
                bool(urun_dict.get("is_remote_run", False)),
            )
            urgap.utl.increase_counter("urgap_node_execution")

        starting_time = time.time()
        self.utrace_history.append(ut.id)

        reasons = ut.evaluate_if_rerun_is_required()
        ut.info()
        self._add_rerun_events(reasons)

        if len(reasons) > 0:
            ut.set_start_time()
            ut = self.execute_rerun(
                utrace=ut,
                starting_time=starting_time,
            )
        else:
            ut.fix_dynamic_output_file_names()
            ut.set_start_time()
            ut.set_stop_time(skipped=True)

        if not hasattr(ut, "duration_seconds"):
            ut.set_stop_time()

        ut.save_umeta_information()

        if ut.urun_dict.unode_parameters["remove_temporary_files"] is True:
            self.delete_tmp_files()

        msg = f"Finished execution of {self.META_INFO['name']} node with utrace.id {ut.id}"
        logger.info(msg)
        logger.info("+------------ ----  -----------------")

        return ut.output_files

    def _open_execution_span(
        self,
        urun_dict: urgap.URunDict,
        utrace: urgap.UTrace,
    ) -> None:
        """Annotate the current tracing span for a local node execution.

        Adds the attributes "wid", "is_remote_run", and "utrace.output_files_stem"
        to the *active* decorator-managed span and increments the
        "urgap_node_execution" counter. If no span is active, it does nothing.

        Args:
            urun_dict (urgap.URunDict): Runtime configuration for the current run.
            utrace (urgap.UTrace): Execution context for this run.
        """
        span = _ot.get_current_span() if _OPENTELEMETRY_AVAILABLE else None
        if span is not None and span.is_recording():
            span.set_attribute("wid", urun_dict.wid)
            span.set_attribute(
                "is_remote_run",
                bool(urun_dict.get("is_remote_run", False)),
            )
            span.set_attribute("utrace.output_files_stem", utrace.output_files_stem)
        urgap.utl.increase_counter("urgap_node_execution")

    @staticmethod
    def _add_rerun_events(reasons: list) -> None:
        span = _ot.get_current_span() if _OPENTELEMETRY_AVAILABLE else None
        if span is None or not span.is_recording():
            return
        if len(reasons) == 0:
            span.add_event("Run was skipped")
        else:
            for reason in reasons:
                span.add_event(f"Reason run is executed: {reason}")

    def execute_rerun(
        self,
        utrace: urgap.UTrace,
        starting_time: float,
    ) -> urgap.UTrace:
        """Execute a rerun of the node if required.

        Args:
            utrace: Combination of urun_dict, ufile_list, and unode.meta.
            starting_time: Time (as float) when execution started.

        Returns:
            The modified UTrace object after rerun.
        """
        utrace.set_start_time()
        flight_sequence = ["preflight", "execute", "postflight"]
        for flight_stage in flight_sequence:
            if hasattr(self, flight_stage) is False:
                msg = f"Skipping {flight_stage} as it is not defined ..."
                logger.info(msg)
                continue

            stage_function = getattr(self, flight_stage)

            msg = f"Running {flight_stage} ..."

            logger.info(msg)
            utrace = stage_function(utrace)
            if isinstance(utrace, urgap.URunDict | urgap.UTrace) is False:
                logger.warning("Wrapper did not return URunDict as second element!")
                raise TypeError
        for output_ufile in utrace.output_files:
            if output_ufile is None:
                continue
            if not output_ufile.io.scratch_path.exists():
                msg = f"Expected output file not found in scratch path {output_ufile.io.scratch_path}."
                raise FileNotFoundError(msg)
        utrace.fix_dynamic_output_file_names()
        execution_time = time.time() - starting_time
        if (
            utrace.urun_dict.unode_parameters["file_io_timeout"] is not None
            and execution_time >= utrace.urun_dict.unode_parameters["file_io_timeout"]
        ):
            msg = (
                f"Node execution took {execution_time:.3f} seconds which is"
                f" longer than the timeout value {utrace.urun_dict['file_io_timeout']}."
                "Therefore re-initializing IO classes for all UFiles."
            )
            logger.info(msg)
            utrace.output_files = urgap.UFileList.from_uri_list(
                utrace.output_files.as_uri_list(),
            )
        utrace.upload_output_files()
        return utrace

    def _pre_checks(self) -> None:
        """Run pre-checks for UNode dependencies.

        - Check if all required 3rd party tools are installed.
        - Check if UMETA["input_uftypes"] are set properly.
        - Initialize self.tmp_files for later deletion.
        """
        if self.has_all_required_installations() is False:
            msg = (
                f"Cannot execute {self.META_INFO['name']}, "
                f"it requires {self.required_3rd_party_installation} "
                "which not available on this system ..."
            )
            logger.info(msg)
            return

        for uftype_spec in itertools.chain(
            self.META_INFO.get("input_uftypes").values(),
            self.META_INFO.get("output_uftypes").values(),
        ):
            if set(uftype_spec.keys()) != {"min", "max"}:
                logger.warning(
                    "uftype specifications should be set explicitly ('min' & 'max')! Please set to -1",
                )
        self.tmp_files = []

    def _construct_exe_path_u2(self) -> Path | None:
        """Construct the executable path for platform-independent and platform-specific engines.

        Returns:
            The constructed Path object to the executable, or None if not found.
        """
        custom_exe_path = self.META_INFO.get("exe_path", None)
        if self.META_INFO["platform_independent"] is True:
            base_path = (
                Path(urgap.home)
                / "resources"
                / "platform_independent"
                / "arc_independent"
            )
            try:
                rel_exe_path = (
                    Path(self.META_INFO["name"])
                    / self.META_INFO["engine"]["platform_independent"][
                        "arc_independent"
                    ]["exe"]
                )
            except KeyError:
                rel_exe_path = None
        else:
            sys_platform = sys.platform
            comp_arch = self.get_comp_arch()
            base_path = Path(urgap.home) / "resources" / sys_platform / comp_arch
            try:
                rel_exe_path = (
                    Path(self.META_INFO["name"])
                    / (self.META_INFO["engine"][sys_platform][comp_arch]["exe"])
                )
            except KeyError:
                msg = f"Your platform ({sys_platform} {comp_arch}) does not seem to be supported by {self.META_INFO['name']}."
                logger.debug(msg)
                rel_exe_path = ""

        if self.META_INFO["engine"].get("system", None) is not None:
            path_to_system_exe = shutil.which(self.META_INFO["engine"]["system"])
            if path_to_system_exe is not None:
                exe_path = Path(path_to_system_exe)
            else:
                exe_path = None
        elif custom_exe_path is not None:
            exe_path = base_path / custom_exe_path
        else:
            exe_path = base_path / rel_exe_path

        if exe_path is not None:
            return Path(exe_path)
        return None

    def construct_exe_path(self) -> os.PathLike | None:
        """Construct the path to the engine executable based on META_INFO.

        Returns:
            Path to the engine executable file, or None if not found.
        """
        if self.META_INFO["unode_version"] is None:
            return self._construct_exe_path_u2()
        if self.META_INFO["unode_version"] == "latest":
            return self._construct_latest_exe_path()
        return self._construct_exe_path_u3()

    def _construct_latest_exe_path(self) -> Path:
        """Construct the path for the latest version of the engine.

        Returns:
            Path object to the latest engine executable.

        Raises:
            RuntimeError: If latest_exe_paths is not set or system binary not found.
        """
        if self.latest_exe_paths is None:
            msg = (
                "If latest is used, exp_path must be set in "
                "urun_dict['unode_parameters']['latest_exe_paths']"
            )
            raise RuntimeError(msg)
        if str(self.latest_exe_paths).startswith("$"):
            _p = shutil.which(self.latest_exe_paths.lstrip("$"))
            if _p is None:
                msg = f"System resource {self.latest_exe_paths} not found on PATH"
                raise RuntimeError(msg)
            exe_path = Path(_p)
            msg = f"Using system resource {self.latest_exe_paths} as exe path"
            logger.info(msg)
        else:
            exe_path = self.latest_exe_paths
        return Path(exe_path)

    def _construct_exe_path_u3(self) -> os.PathLike | None:
        """Construct the path to the executable for a specific tagged version.

        Returns:
            Path to the executable for the specified version, or None if not found.

        Raises:
            RuntimeError: If version or exe_path information is missing.
        """
        base_path = Path(urgap.home) / "resources"
        tagged_exe_path = None
        version_info = None
        for v in self.META_INFO["versions"]:
            if v["version"] == self.META_INFO["unode_version"]:
                version_info = v
                break
        if version_info is None:
            msg = f"{self.META_INFO['unode_version']} is not specified in UNode"
            raise RuntimeError(msg)
        if version_info.get("exe_path", None) is None:
            msg = (
                f"Tag {self.META_INFO['unode_version']} has not exe_path entry in UMETA"
            )
            raise RuntimeError(msg)
        if version_info["exe_path"].startswith("$"):
            path_to_system_resource = shutil.which(version_info["exe_path"].lstrip("$"))
            if path_to_system_resource is not None:
                tagged_exe_path = Path(path_to_system_resource)
        else:
            tagged_exe_path = base_path / Path(version_info["exe_path"])
            if tagged_exe_path.exists() is False:
                tagged_exe_path = None
        if tagged_exe_path is not None:
            return tagged_exe_path
        return None

    @property
    def resource_subfolder(self) -> str:
        """Get the resource subfolder for this node.

        Returns:
            Resource subfolder as a string.
        """
        if self.META_INFO.get("platform_independent", True) is True:
            subfolder = "platform_independent/arc_independent"
        else:
            subfolder = f"{sys.platform}/{self.get_comp_arch()}"
        return subfolder

    def get_comp_arch(self) -> str:
        """Get the computer architecture string.

        Note:
            platform.machine() outcomes on different platforms:
              - Darwin returns either arm64 or x86_64.
              - Linux returns either aarch64 or x86_64.
              - Windows should always be x86_64.

        Returns:
            Computer architecture, either "arm64" or "x86_64".
        """
        comp_platform = sys.platform
        comp_arch = platform.machine()
        if comp_platform == "win32" or comp_platform.startswith("linux"):
            return "x86_64"
        if comp_arch == "arm64":
            return comp_arch
        return "x86_64"

    def install_resource(
        self,
        remote_ufile: urgap.UFile,
        engine_exe_list: list,
    ) -> bool | None:
        """Install the given resource package and set correct permissions on executables.

        Args:
            remote_ufile: Urgap resource package file to be installed.
            engine_exe_list: List of expected executable names.

        Returns:
            True if successfully installed, otherwise None.
        """
        urgap_resource_dir = urgap.home / "resources" / self.resource_subfolder
        try:
            new_ufiles = remote_ufile.uncompress()
        except (FileNotFoundError, NotImplementedError) as e:
            if isinstance(e, FileNotFoundError):
                logger.warning("Resource package not found...")
            elif isinstance(e, NotImplementedError):
                logger.warning("Resource package cannot be uncompressed...")
            return None

        pure_engine_exe_list = [Path(x).name for x in engine_exe_list]
        for uf in new_ufiles:
            uf.rebase(f"file://{urgap_resource_dir}", upload=True)
            if uf.path.name in pure_engine_exe_list:
                Path(uf.io.remote_path).chmod(stat.S_IRWXU)
            uf.purge_local()
        return True

    def check_if_all_exe_exist(self, engine_exe_list: list) -> bool:
        """Check if all required executables exist for the current node.

        Args:
            engine_exe_list: List of executable filenames.

        Returns:
            True if all executables are available, otherwise False.
        """
        missing_exe = []
        if "exe_path" in self.META_INFO:
            exe_exists = self.exe_path.exists() and self.exe_path.is_file()
            if exe_exists is False:
                missing_exe.append(str(self.exe_path))
        else:
            for exe in engine_exe_list:
                path = self.exe_path.parent.joinpath(exe)

                if (path.exists() and path.is_file()) is False:
                    missing_exe.append(exe)

        if len(missing_exe) != 0:
            msg = f"The following executables are missing: {','.join(missing_exe)}"
            logger.info(msg)
            return False
        return True

    def delete_tmp_files(self) -> None:
        """Delete temporary files created during node execution.

        Note:
            Files with paths containing ".", "/", "./", or "../" will not be deleted for safety.
        """
        msg = f"Removing tmp_files ... {self.tmp_files}"
        logger.debug(msg)
        self.tmp_files = [Path(p) for p in self.tmp_files]
        for path in self.tmp_files:
            if str(path) in [".", "/", "./", "../"]:
                msg = f"Not deleting {path}, might be unsafe"
                logger.info(msg)
                continue
            if path.exists():
                if path.is_dir():
                    if path.is_symlink():
                        path.unlink()
                    else:
                        shutil.rmtree(path)
                else:
                    path.unlink()
        self.tmp_files = []

    def has_all_required_installations(self) -> bool:
        """Check if all required 3rd party installations are present for this node.

        Returns:
            True if all required 3rd party installations are available, otherwise False.
        """
        return urgap.instances.unode_manager.node_availability_lookup[
            self.META_INFO["unode_full_identifier"]
        ]["requirements_available"]

    def remove_output_folder(self, output_file: urgap.UFile = None) -> None:
        """Remove the output folder for the specified output_file.

        Args:
            output_file: UFile for which the output folder should be removed.
        """
        output_file.remove_remote_object()

    def remove_umeta(self, output_file: urgap.UFile = None) -> None:
        """Remove umeta data for a given output_file.

        Args:
            output_file: UFile for which umeta should be removed.
        """
        umeta = urgap.UMeta()
        msg = f"Removing {output_file}"
        logger.debug(msg)

        umeta.delete(output_file)

    @property
    def required_3rd_party_installation(self) -> dict | None:
        """Get required 3rd party installations for this node.

        Returns:
            Dictionary with 3rd party tool and version, or None if not required.
        """
        return self.META_INFO.get("requires", None)

    @classmethod
    def generate_node_vis(cls, ufile: urgap.UFile) -> list:
        """Generate basic node-specific data visualization structure.

        Note: For example::
            data = [
                {
                    "section_title": "",
                    "section_text": "",
                    "networks": [
                        {
                            "title": "",
                            "links": "",
                            "caption" :"".
                        }
                    ]
                    "figures": [
                        {
                            "title": "",
                            "data": "",
                            "_type": "html|img",
                            "caption": "",
                        }
                    ],
                    "tables": [
                        {
                            "title": "",
                            "headers": "",
                            "rows": [],
                            "caption":""
                        }
                    ],
                }
            ]

        Args:
            ufile: Urgap resource package file.

        Returns:
            List with visualization data (tables, figures, etc) describing the node.
        """
        um = urgap.UMeta(ufile=ufile, load_umeta=True)
        data = [
            {
                "section_title": "General Node Info",
                "tables": [
                    {
                        "title": "Run information",
                        "headers": ["key", "value"],
                        "rows": [
                            {
                                "key": "Urgap version",
                                "value": f"{um.urun_dict['version']}",
                            },
                        ],
                        "caption": "URun Dict information associated with the file",
                    },
                ],
            },
        ]
        for k in ["input_files", "output_files"]:
            for entry in um.urun_dict.get(k, []):
                data[0]["tables"][0]["rows"].append(
                    {"key": k, "value": entry.object_name},
                )

        for wid, _object_name in um.history:
            data[0]["tables"][0]["rows"].append({"key": "@wid", "value": wid})

        data[0]["tables"].append(
            {
                "title": "Parameters",
                "headers": ["key", "value"],
                "rows": [
                    {"key": k, "value": v}
                    for k, v in um.urun_dict["parameters"].items()
                ],
                "caption": "Urgap style Parameters used to create this file",
            },
        )
        if hasattr(cls, "generate_wrapper_vis") and callable(cls.generate_wrapper_vis):
            data += cls.generate_wrapper_vis(ufile)
        return data

    @utl_trace(
        span_name="unode.execute",
        attributes={"component": "unode"},
        attrs_from=lambda a, _kw: {
            "wid": a[1].urun_dict.wid,
            "unode_full_identifier": a[1].unode_meta["unode_full_identifier"],
        },
    )
    def execute(self, utrace: urgap.UTrace) -> urgap.UTrace:
        """Execute method for a node using subprocess.run.

        Args:
            utrace: Combination of urun_dict, ufile_list, and unode.meta.

        Returns:
            The updated UTrace after execution.

        Raises:
            KeyError: If no command_list is found in urun_dict.
        """
        if "command_list" not in utrace.urun_dict.unode_rinfo:
            msg = (
                "No command_list was found in urun_dict."
                "Convention is to define the command list during "
                "preflight in the UNode engine class."
            )
            raise KeyError(msg)

        utrace.urun_dict.command_list = [str(x) for x in utrace.urun_dict.command_list]
        cmd_msg = f"Executing command list: {' '.join(utrace.urun_dict.command_list)}"
        logger.info(cmd_msg)

        span = _ot.get_current_span() if _OPENTELEMETRY_AVAILABLE else None
        if span is not None and span.is_recording():
            span.set_attribute("unode.command", " ".join(utrace.urun_dict.command_list))
            span.add_event(cmd_msg)

        execute_answer = []
        proc = None
        if len(utrace.urun_dict.command_list) != 0:
            proc = subprocess.run(
                utrace.urun_dict.command_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
        else:
            logger.info("Command list is empty, nothing to do here...")
            execute_answer.append("Command list is empty")

        utrace, msg = self._check_proc_outcome(
            proc=proc,
            execute_answer=execute_answer,
            utrace=utrace,
        )

        if span is not None and span.is_recording():
            if proc is not None:
                span.set_attribute("unode.return_code", int(proc.returncode))
            for line in msg.split("\n"):
                if line:
                    span.add_event(line)

        logger.info("Finished executing command list ...")
        return utrace

    def _check_proc_outcome(
        self,
        proc: subprocess.CompletedProcess,
        execute_answer: list,
        utrace: urgap.UTrace,
    ) -> tuple[urgap.UTrace, str]:
        """Check the outcome of the executed process and handle output.

        Args:
            proc: The CompletedProcess from subprocess.run (or None if nothing was executed).
            execute_answer: List to store stdout lines.
            utrace: The UTrace for this execution.

        Returns:
            Tuple of the updated UTrace and a summary message.

        Raises:
            RuntimeError: If process failed and crash_on_resource_crash is True.
        """
        msg = ""
        if (proc is not None) and (proc.stdout is not None):
            for line in proc.stdout.split("\n"):
                try:
                    logger.info(line)
                    execute_answer.append(line)
                except ValueError:
                    logger.info(
                        "stdout Line skipped as it cannot be reformatted with logger",
                    )

        if proc is None:
            logger.warning(
                "Process was not executed (proc is None). Marking trace as stopped.",
            )
            return None

        if proc.returncode != 0:
            msg = (
                f"Node {self.META_INFO['name']} finished with exit code {proc.returncode}!\n"
                f"Command: {' '.join(utrace.urun_dict.command_list)}\n"
                f"Input Files: {[uf.object_name for uf in utrace.input_files]}\n"
                f"Output Files: {[uf.object_name for uf in utrace.output_files]}\n"
                f"StdOut: \n"
            )
            for line in execute_answer:
                msg += line + "\n"
            logger.error(msg)
            utrace.output_files = urgap.UFileList([None])
            utrace.set_stop_time(crashed=True)
            if utrace.urun_dict.unode_parameters["crash_on_resource_crash"] is True:
                raise RuntimeError(msg)
        else:
            utrace.set_stop_time()
        return utrace, msg
