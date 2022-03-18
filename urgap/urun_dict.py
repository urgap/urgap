import copy
import json
from collections import UserDict



class URunDict(UserDict):





    """

        super().__init__(*args, **kwargs)
        self._storage_requirements = {
            "parameters": {},
            "user_dict": {},
            "unode_parameters": {
                "additional_filters": None,
                "dry_run": False,
                "force": False,
                "override_folder_creation": False,
                "prefix": None,
                "record_skipped_runs": False,
                "remove_temporary_files": False,
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


    @property

    @property



        """
        if rerun_only:
        else:
        tmp_json = json.dumps(
        )
        sorted_json = json.dumps(
        )

    def _generate_container_folder_name(
        if run_folder_name is None:
        else:
            container_folder_name = run_folder_name

        if skip_data_versioning is False:
        return container_folder_name

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
