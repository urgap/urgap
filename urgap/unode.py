"""Unode class.

This module defines the UnodeBase class, which is inherited by wrappers.
"""

import copy
import itertools
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path




        self._exe_path = None
        self.status = None
        self.tmp_files = []
        self.utrace_history = []

    @property
    def exe_path(self) -> os.PathLike:

        Returns:
        """
        if self._exe_path is None:
        return self._exe_path

    @property
    def resource_is_available(self) -> bool:

        Note:

        Returns:
        """
        ]["resource_available"]

    @property
    def requires_3rd_party_installation(self) -> bool:

        Returns:
        """
        ]["has_3rd_party_requirements"]

    def run(
        self,
            msg = "UNode.run() function requires URunDict."
            raise TypeError(msg)
        urun_dict = copy.deepcopy(urun_dict)
        if urun_dict.unode_parameters["skip_pre_checks"] is False:
            self._pre_checks()

        self.tmp_files = []
            urun_dict.unode_parameters.update(kwargs)

            urun_dict=urun_dict,
            input_files=ufiles,
            unode_meta=self.META_INFO,
        )
        starting_time = time.time()
        self.utrace_history.append(ut.id)
        reasons = ut.evaluate_if_rerun_is_required()
        ut.info()
        if len(reasons) > 0:
        else:
            ut.fix_dynamic_output_file_names()
        ut.save_umeta_information()
        if ut.urun_dict.unode_parameters["remove_temporary_files"] is True:
            self.delete_tmp_files()

        return ut.output_files


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
        elif custom_exe_path is not None:
            exe_path = base_path / custom_exe_path
        else:
            exe_path = base_path / rel_exe_path


        Returns:
        """

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


        Returns:
        """


        Args:
        """

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
        if proc.returncode != 0:
            msg = (
                f"Node {self.META_INFO['name']} finished with exit code {proc.returncode}!\n"
                f"Command: {' '.join(utrace.urun_dict.command_list)}\n"
                f"Input Files: {[uf.object_name for uf in utrace.input_files]}\n"
            )
            if utrace.urun_dict.unode_parameters["crash_on_resource_crash"] is True:
                raise RuntimeError(msg)