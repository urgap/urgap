
import json
import logging
import re
import tempfile

from pathlib import Path



omiq_api_available = True


class IOOmiq(UIOBase):


        Args:
        """
        self._omiq_user_info = None
        self._file_id = None
        self._tags = None

        password = um.get_password(cred_key)
        user = um.get_user(cred_key)
        with tempfile.NamedTemporaryFile() as fp:
                json.dump(
                    {
                        "token": password,
                        "email": user,
                    },
                    tmp_file,
                )
            self._omiq_user_info = self._api.get_user()
            if self._omiq_user_info is not None:
                msg = "Authenticated to OMIQ API as {name} [last login:{lastLoginTime}]".format(
                )
        self._workflow = self._api.get_workflow(self._workflow_id)
        self._dataset_id = int(self._workflow["datasetId"])
        if self._query_params.get("derived_from_fcs", False) is True:
            self._corresponding_fcs_filename = str(
            )
        else:
            self._corresponding_fcs_filename = None
        self._scratch_path = self.scratch_path

    @property
    def remote_path(self) -> str | None:

        Returns:
        """
        return None

    @property
    def remote_tag_path(self) -> str | None:

        Returns:
        """
        return None

    def get_remote_tags(self) -> dict | None:

        Returns:
        """
        if self._tags is not None:
            return self._tags

        keys_to_grab = [
            "id",
            "datasetId",
            "fileName",
            "displayName",
            "rawFileBlobId",
            "jobName",
            "status",
            "size",
            "features",
        ]
        self._tags = {"omiq_tags": True}
        for file_dict in self._list_files_in_dataset():
            if (
                or file_dict["displayName"] == self._corresponding_fcs_filename
            ):
                for key in keys_to_grab:
                    file_value = file_dict.get(key, None)
                    if file_value is None:
                        msg = f"OMIQ API does not provide {key}"
                    self._tags[key] = file_dict.get(key, None)
        return self._tags

    def download(self) -> None:
        if self._corresponding_fcs_filename is not None:
            self._handle_derived_fcs()
        elif (
            self._query_params.get("uftype", None)
        ):
            self._download_file_from_workflow()
            i["displayName"] for i in self._list_files_in_dataset()
        ]:
            self._download_file_from_dataset()
            self._download_file_from_artifacts()
        else:
            self._handle_file_not_found()

        self._api.upload_files_to_dataset(self._dataset_id, [self.scratch_path])

    def _handle_derived_fcs(self) -> None:
        file_id = self.file_id
        if file_id is None:
            raise FileNotFoundError(msg)
        self._set_query_params(file_id)
        relevant_keys = (
            "dataset_id",
            "file_id",
            "feature_names",
            "add_row_nums",
            "filter_ids",
            "workflow",
            "from_task_id",
            "filepath",
            "filter_usage_mode",
            "drop_not_filtered",
            "reverse_scaling",
            "overwrite",
            "verbose",
        )
        self._api.export_data(
        )

    def _set_query_params(self, file_id: str) -> None:
        self._query_params["filter_usage_mode"] = self._query_params.get(
        )
        self._query_params["dataset_id"] = self._dataset_id
        self._query_params["file_id"] = file_id
        self._query_params["filepath"] = Path(str(self.scratch_path).split("?")[0])
        self._query_params["add_row_nums"] = self._query_params.get(
        )
        self._query_params["reverse_scaling"] = self._query_params.get(
        )
        self._query_params["workflow"] = self._workflow
        self._query_params["feature_names"] = [ftr["name"] for ftr in self.features]
        self._set_optional_task_and_filter_params()

    def _set_optional_task_and_filter_params(self) -> None:
        if "from_task_id" not in self._query_params:
            self._set_from_task_id()
        if "filter_ids" not in self._query_params:
            self._query_params["filter_ids"] = omiq_api.get_available_filters(
            )

    def _set_from_task_id(self) -> None:
        for task in self._workflow["tasks"]:
            if task.get("type") == "GatingTask":
                self._query_params["from_task_id"] = int(task["id"])
                break

    def _download_file_from_dataset(self) -> None:
        self._api.download_file(
            dataset_id=self._dataset_id,
            file_id=self.file_id,
            filepath=self._scratch_path,
        )

    def _download_file_from_artifacts(self) -> None:
        self._api.download_artifact(
            task_id=task_id,
            filepath=self._scratch_path,
        )

    def _download_file_from_workflow(self) -> None:
        dict_workflow = {"dataset": self._dataset_id, "workflow": self._workflow}
            json.dump(dict_workflow, gfile, indent=4)

    def _get_task_id_for_artifact(self, filename: str) -> str:
        return next(
            i["taskId"]
            for i in self._workflow.get("taskArtifacts", [])
            if i["file"] == filename
        )

    def _handle_file_not_found(self) -> None:
        if self._corresponding_fcs_filename is None:
        else:
            f = self._corresponding_fcs_filename
        raise FileNotFoundError(msg)

    @property
    def file_id(self) -> int:
        tags = self.get_remote_tags()
        return tags["id"]

    @property
    def features(self) -> dict:
        tags = self.get_remote_tags()
        return tags["features"]

    def _list_files_in_dataset(self) -> list:
        return self._api.list_files_in_dataset(self._dataset_id)

    def _list_artifacts(self) -> list:
        return [i["file"] for i in self._workflow.get("taskArtifacts", [])]

    def list_container_items(
        self,
        pattern: str | None = None,
    ) -> list:

        Args:

        Returns:
        """
        if pattern is not None:
            container_objects = [
                name
                for name in container_objects
                if re.search(pattern, name) is not None
            ]
        return container_objects

    def remote_object_exists(self) -> bool:

        Returns:
        """
        return (
            or self._corresponding_fcs_filename in self._list_artifacts()
        )