
import copy
import json
import logging
from collections import UserDict



class URunDict(UserDict):





    """



        """
        super().__init__(*args, **kwargs)
        self._storage_requirements = {
            "parameters": {},
            "user_dict": {},
            "unode_parameters": {
                "additional_filters": None,
                "crash_on_resource_crash": True,
                "dry_run": False,
                "file_io_timeout": None,
                "force": False,
                "override_folder_creation": False,
                "prefix": None,
                "record_skipped_runs": False,
                "remote_execution_timeout": 7200,  # 2h
                "remote_url": None,
                "remove_temporary_files": False,
                "retain_uftype": False,
                "run_folder_name": None,
                "run_resource_as": "subprocess_run",
                "skip_data_versioning": False,
                "skip_pre_checks": False,
                "storage_base_uri": None,
                "latest_exe_paths": {},
            },
        }
        self._default_setup_that_cannot_be_set_by_user = {
            "input_files": None,
            "output_files": None,
            "unode_rinfo": {
                "command_list": [],
                "rerun_reasons": [],
            },
        }
        for k, v in self._storage_requirements.items():
            if k not in self.keys():
                self[k] = {}
            for k2, v2 in v.items():
                    self[k][k2] = v2

        for k, v in self._default_setup_that_cannot_be_set_by_user.items():
            self.assign_wid()

        default_storage_parameters = copy.deepcopy(
        )
        default_storage_parameters.update(user_dict)
        return default_storage_parameters

    @property
    def wid(self) -> str:

        Returns:
        """
        return self["wid"]

    @wid.setter

        Args:
        """
        self["wid"] = wid


        self.assign_wid()

    @property
    def parameters(self) -> dict:
        """Get wrapper parameters.

        Returns:
        """
        return self.get("parameters", {})

    @parameters.setter

        Args:
        """
        self["parameters"] = parameters

    @property
    def user_dict(self) -> dict:

        Returns:
        """
        return self.get("user_dict", {})

    @user_dict.setter

        Args:
        """
        self["user_dict"] = user_dict

    @property
    def unode_parameters(self) -> dict:

        Returns:
        """
        return self["unode_parameters"]

    @unode_parameters.setter

        Args:
        """
        if isinstance(unode_parameters, dict) is False:

        self["unode_parameters"] = self._update_default_storage(
        )

    @property
    def unode_rinfo(self) -> dict:

        Returns:
        """
        return self["unode_rinfo"]

    @unode_rinfo.setter

        Args:
        """
        if isinstance(unode_rinfo, dict) is False:
        self["unode_rinfo"] = self._update_default_storage("unode_rinfo", unode_rinfo)

    @property
    def meta_info(self) -> dict:

        Returns:
        """
        return self.unode_rinfo["meta_info"]

    @meta_info.setter

        Args:
        """
        self.unode_rinfo["meta_info"] = meta_info

    @property

        Returns:
        """
        return self.data["input_files"]

    @input_files.setter

        Args:

        Raises:
        """
        self.data["input_files"] = input_files

    @property

        Returns:
        """
        return self.data["output_files"]

    @output_files.setter

        Args:

        Raises:
        """
        self.data["output_files"] = output_files

    @property
    def command_list(self) -> list:

        Returns:
        """
        return self.unode_rinfo["command_list"]

    @command_list.setter

        Args:

        Raises:
        """
        if isinstance(command_list, list) is False:
        self.unode_rinfo["command_list"] = command_list

    @property

        Returns:
        """

    @property

        Returns:
        """



        """
        if rerun_only:
        else:
        tmp_json = json.dumps(
        )
        sorted_json = json.dumps(
        )

    def _generate_container_folder_name(
        self,
        if run_folder_name is None:
                self.unode_rinfo["meta_info"]["name"],
                self.unode_rinfo["meta_info"]["wrapper_version"]["major"],
            )
        else:
            container_folder_name = run_folder_name

        if skip_data_versioning is False:
        return container_folder_name

        """Determine the root folder for output files.


        Args:
            ufiles: List of UFiles.

        Returns:
            Path to output file stem.
        """
        if ufiles is None:
            ufiles = self.input_files

        if ufiles is None or len(ufiles) == 0:
        self.data["object_folder"] = self._generate_container_folder_name(
            skip_data_versioning=self.unode_parameters["skip_data_versioning"],
            run_folder_name=self.unode_parameters["run_folder_name"],
        )

        if self.unode_parameters["prefix"] is not None:

        if self.unode_parameters["override_folder_creation"] is True:
        else:
        return new_fragment


        Args:
        """