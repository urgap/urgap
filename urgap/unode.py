"""Unode class.

This module defines the UnodeBase class, which is inherited by wrappers.
"""

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
from pathlib import Path





        self._exe_path = None
        self.status = None
        self.tmp_files = []
        self.utrace_history = []
        self.latest_exe_paths = None

    @property
    def exe_path(self) -> os.PathLike:

        Returns:
        """
        if self._exe_path is None:
            self._exe_path = self.construct_exe_path()
        return self._exe_path

    @property
    def resource_is_available(self) -> bool:

        Note:

        Returns:
        """
            self.META_INFO["unode_full_identifier"]
        ]["resource_available"]

    @property
    def requires_3rd_party_installation(self) -> bool:

        Returns:
        """
            self.META_INFO["unode_full_identifier"]
        ]["has_3rd_party_requirements"]

    def run(
        self,
            msg = "UNode.run() function requires URunDict."
            raise TypeError(msg)
        urun_dict = copy.deepcopy(urun_dict)


        if urun_dict.unode_parameters["skip_pre_checks"] is False:
            self._pre_checks()

        self.tmp_files = []
        if len(kwargs.keys()) != 0:
            urun_dict.unode_parameters.update(kwargs)

        if urun_dict["unode_parameters"]["remote_url"] is None:
            output_files = self._run_locally(ufiles=ufiles, urun_dict=urun_dict)
        else:
            output_files = self._run_remotely(ufiles=ufiles, urun_dict=urun_dict)

        return output_files

    def _run_remotely(
        self,
        urun_dict["is_remote_run"] = True
        try:
            response = requests.post(
                remote_url,
                timeout=urun_dict["unode_parameters"]["remote_execution_timeout"],
            )
                span.set_attribute("exception.type", type(e).__name__)
                span.set_attribute("exception.message", str(e))

    def _run_locally(
        self,
            if all(isinstance(file, str) for file in ufiles):
            else:
        ufiles = ufiles.create_flat_and_non_redundant_list()
            urun_dict=urun_dict,
            input_files=ufiles,
            unode_meta=self.META_INFO,
            unode_version=self.META_INFO["unode_version"],
        )
        starting_time = time.time()
        self.utrace_history.append(ut.id)
        reasons = ut.evaluate_if_rerun_is_required()
        ut.info()
        if len(reasons) > 0:
            ut = self.execute_rerun(
                utrace=ut,
                starting_time=starting_time,
            )
        else:
            ut.fix_dynamic_output_file_names()
        ut.save_umeta_information()
        if ut.urun_dict.unode_parameters["remove_temporary_files"] is True:
            self.delete_tmp_files()

        return ut.output_files

    def _open_execution_span(
        self,
            )

        if len(reasons) == 0:
        else:
            for reason in reasons:

    def execute_rerun(
        self,
        starting_time: float,

        Args:

        Returns:
        """
        flight_sequence = ["preflight", "execute", "postflight"]
        for flight_stage in flight_sequence:
            if hasattr(self, flight_stage) is False:
                continue

            stage_function = getattr(self, flight_stage)

            utrace = stage_function(utrace)
                raise TypeError
        utrace.fix_dynamic_output_file_names()
        execution_time = time.time() - starting_time
        if (
            utrace.urun_dict.unode_parameters["file_io_timeout"] is not None
            and execution_time >= utrace.urun_dict.unode_parameters["file_io_timeout"]
        ):
                f"Node execution took {execution_time:.3f} seconds which is"
                f" longer than the timeout value {utrace.urun_dict['file_io_timeout']}."
                "Therefore re-initializing IO classes for all UFiles."
            )
            )
        utrace.upload_output_files()
        return utrace


        """
        if self.has_all_required_installations() is False:
                f"Cannot execute {self.META_INFO['name']}, "
                f"it requires {self.required_3rd_party_installation} "
                "which not available on this system ..."
            )

        for uftype_spec in itertools.chain(
            self.META_INFO.get("input_uftypes").values(),
            self.META_INFO.get("output_uftypes").values(),
        ):
                )
        self.tmp_files = []

        custom_exe_path = self.META_INFO.get("exe_path", None)
        if self.META_INFO["platform_independent"] is True:
            base_path = (
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
            try:
                )
            except KeyError:
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

        Returns:
        """
        if self.META_INFO["unode_version"] is None:
            return self._construct_exe_path_u2()
            return self._construct_latest_exe_path()

        if self.latest_exe_paths is None:
                "If latest is used, exp_path must be set in "
                "urun_dict['unode_parameters']['latest_exe_paths']"
            )
        else:
            exe_path = self.latest_exe_paths
        return Path(exe_path)

    def _construct_exe_path_u3(self) -> os.PathLike | None:
        tagged_exe_path = None
        version_info = None
        for v in self.META_INFO["versions"]:
            if v["version"] == self.META_INFO["unode_version"]:
                version_info = v
                break
        if version_info is None:
        if version_info.get("exe_path", None) is None:
            )
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

    @property
    def resource_subfolder(self) -> str:

        Returns:
        """
        if self.META_INFO.get("platform_independent", True) is True:
            subfolder = "platform_independent/arc_independent"
        else:
            subfolder = f"{sys.platform}/{self.get_comp_arch()}"
        return subfolder

    def get_comp_arch(self) -> str:

        Note:
            platform.machine() outcomes on different platforms:

        Returns:
        """
        comp_platform = sys.platform
        comp_arch = platform.machine()
            return "x86_64"

    def install_resource(
        self,
        engine_exe_list: list,

        Args:

        Returns:
        """
        try:
            new_ufiles = remote_ufile.uncompress()
        except (FileNotFoundError, NotImplementedError) as e:
            if isinstance(e, FileNotFoundError):
            elif isinstance(e, NotImplementedError):
            return None

        pure_engine_exe_list = [Path(x).name for x in engine_exe_list]
        for uf in new_ufiles:
            if uf.path.name in pure_engine_exe_list:
            uf.purge_local()
        return True

    def check_if_all_exe_exist(self, engine_exe_list: list) -> bool:

        Args:

        Returns:
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
            return False


        Note:
        """
        for path in self.tmp_files:
            if str(path) in [".", "/", "./", "../"]:
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

        Returns:
        """
            self.META_INFO["unode_full_identifier"]
        ]["requirements_available"]


        Args:
        """
        output_file.remove_remote_object()

        """Remove umeta data for a given output_file.

        Args:
        """

        umeta.delete(output_file)

    @property

        Returns:
        """
        return self.META_INFO.get("requires", None)

    @classmethod

        Args:

        Returns:
        """
        data = [
            {
                "section_title": "General Node Info",
                "tables": [
                    {
                        "title": "Run information",
                        "headers": ["key", "value"],
                        "rows": [
                            {
                                "value": f"{um.urun_dict['version']}",
                            },
                        ],
                        "caption": "URun Dict information associated with the file",
                ],
        ]
        for k in ["input_files", "output_files"]:
            for entry in um.urun_dict.get(k, []):
                data[0]["tables"][0]["rows"].append(
                )

            data[0]["tables"][0]["rows"].append({"key": "@wid", "value": wid})

        data[0]["tables"].append(
            {
                "title": "Parameters",
                "headers": ["key", "value"],
                "rows": [
                    {"key": k, "value": v}
                    for k, v in um.urun_dict["parameters"].items()
                ],
        )
            data += cls.generate_wrapper_vis(ufile)
        return data


        Args:

        Returns:

        """
                "No command_list was found in urun_dict."
                "Convention is to define the command list during "
                "preflight in the UNode engine class."
            )

        utrace.urun_dict.command_list = [str(x) for x in utrace.urun_dict.command_list]
        cmd_msg = f"Executing command list: {' '.join(utrace.urun_dict.command_list)}"
        execute_answer = []
        proc = None
        if len(utrace.urun_dict.command_list) != 0:
            proc = subprocess.run(
                utrace.urun_dict.command_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        else:
            execute_answer.append("Command list is empty")
        utrace, msg = self._check_proc_outcome(
            proc=proc,
            execute_answer=execute_answer,
            utrace=utrace,
        )
        return utrace

        msg = ""
        if (proc is not None) and (proc.stdout is not None):
            for line in proc.stdout.split("\n"):
                try:
                    execute_answer.append(line)
                except ValueError:
                    )
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
            if utrace.urun_dict.unode_parameters["crash_on_resource_crash"] is True:
                raise RuntimeError(msg)
        return utrace, msg