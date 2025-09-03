"""Omiq scheme subclass of urgap2's UIO submodule."""

import json
import logging
import re
import tempfile

from pathlib import Path
from typing import ParamSpec

import urgap

from urgap.ext import omiq_api
from urgap.ufile.io._base import UIOBase

P = ParamSpec("P")
omiq_api_available = True
logger = logging.getLogger(__name__)


class IOOmiq(UIOBase):
    """UIO class interface for OMIQ storage and workflows.

    Provides interaction with the OMIQ API for file upload, download, and metadata extraction.
    """

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create a new UIO class for processing OMIQ data.

        Args:
            **kwargs: Passed to UIOBase, includes the uri and configuration keys.
        """
        super().__init__(**kwargs)
        self._omiq_user_info = None
        self._file_id = None
        self._tags = None

        cred_key = f"{self.uuri.scheme}://{self.uuri.netloc}"
        um = urgap.instances.ucredential_manager
        password = um.get_password(cred_key)
        user = um.get_user(cred_key)
        with tempfile.NamedTemporaryFile() as fp:
            with Path(fp.name).open("w") as tmp_file:
                json.dump(
                    {
                        "token": password,
                        "email": user,
                    },
                    tmp_file,
                )
            self._api = omiq_api.API(self.uuri.netloc, secret_filepath=fp.name)
            self._omiq_user_info = self._api.get_user()
            if self._omiq_user_info is not None:
                msg = "Authenticated to OMIQ API as {name} [last login:{lastLoginTime}]".format(
                    **self._omiq_user_info,
                )
                logger.info(msg)
        self._workflow_id = self.uuri.get_container_name()
        self._workflow = self._api.get_workflow(self._workflow_id)
        self._dataset_id = int(self._workflow["datasetId"])
        self._query_params = self.uuri.query
        if self._query_params.get("derived_from_fcs", False) is True:
            self._corresponding_fcs_filename = str(
                Path(self.uuri.fragment).with_suffix(".fcs"),
            )
        else:
            self._corresponding_fcs_filename = None
        self._scratch_path = self.scratch_path

    @property
    def remote_path(self) -> str | None:
        """Get the remote file path.

        Returns:
            None (handled internally by API endpoints).
        """
        return None

    @property
    def remote_tag_path(self) -> str | None:
        """Get the remote file tag path.

        Returns:
            None (handled internally by API endpoints).
        """
        return None

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with the referenced file.

        Only a subset of tags are extracted from the OMIQ API.

        Returns:
            Dictionary of OMIQ metadata tags for the referenced file, or None if not found.
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
                file_dict["displayName"] == self.uuri.fragment
                or file_dict["displayName"] == self._corresponding_fcs_filename
            ):
                for key in keys_to_grab:
                    file_value = file_dict.get(key, None)
                    if file_value is None:
                        msg = f"OMIQ API does not provide {key}"
                        logger.warning(msg)
                    self._tags[key] = file_dict.get(key, None)
        return self._tags

    def download(self) -> None:
        """Download the file to the scratch path from the remote OMIQ location.

        Downloads files or artifacts as needed, or raises FileNotFoundError if not found.
        """
        if self._corresponding_fcs_filename is not None:
            self._handle_derived_fcs()
        elif (
            self._query_params.get("uftype", None)
            == urgap.uftypes.flow_cytometry.gating_strategy.OMIQ_GFILE
        ):
            self._download_file_from_workflow()
        elif self.uuri.fragment in [
            i["displayName"] for i in self._list_files_in_dataset()
        ]:
            self._download_file_from_dataset()
        elif self.uuri.fragment in self._list_artifacts():
            self._download_file_from_artifacts()
        else:
            self._handle_file_not_found()

    def upload(self, tags: dict | None = None) -> None:
        """Upload file to OMIQ dataset.

        Args:
            tags: Tags to upload with the file. (Currently not implemented.)

        Notes:
            Tag upload is not yet implemented.
        """
        if tags is not None:
            logger.warning("Upload of tags is not implemented yet.")
        self._api.upload_files_to_dataset(self._dataset_id, [self.scratch_path])

    def _handle_derived_fcs(self) -> None:
        """Handle the case where the file is derived from an FCS file.

        Raises:
            FileNotFoundError: If the FCS file does not exist in the workflow.
        """
        file_id = self.file_id
        if file_id is None:
            msg = f"file: ({self._corresponding_fcs_filename}) does not exist in workflow: {self.uuri.get_container_name()}"
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
            **{k: v for k, v in self._query_params.items() if k in relevant_keys},
        )

    def _set_query_params(self, file_id: str) -> None:
        """Set query parameters used for file export from OMIQ.

        Args:
            file_id: ID of the file to export.
        """
        self._query_params["filter_usage_mode"] = self._query_params.get(
            "filter_usage_mode",
            "NAMECOL",
        )
        self._query_params["dataset_id"] = self._dataset_id
        self._query_params["file_id"] = file_id
        self._query_params["filepath"] = Path(str(self.scratch_path).split("?")[0])
        self._query_params["add_row_nums"] = self._query_params.get(
            "add_row_nums",
            True,
        )
        self._query_params["reverse_scaling"] = self._query_params.get(
            "reverse_scaling",
            False,
        )
        self._query_params["workflow"] = self._workflow
        self._query_params["feature_names"] = [ftr["name"] for ftr in self.features]
        self._set_optional_task_and_filter_params()

    def _set_optional_task_and_filter_params(self) -> None:
        """Set optional query parameters for 'from_task_id' and 'filter_ids' if missing."""
        if "from_task_id" not in self._query_params:
            self._set_from_task_id()
        if "filter_ids" not in self._query_params:
            self._query_params["filter_ids"] = omiq_api.get_available_filters(
                self._workflow,
                self._query_params["from_task_id"],
            )

    def _set_from_task_id(self) -> None:
        """Set the 'from_task_id' query parameter based on workflow GatingTask."""
        for task in self._workflow["tasks"]:
            if task.get("type") == "GatingTask":
                self._query_params["from_task_id"] = int(task["id"])
                break

    def _download_file_from_dataset(self) -> None:
        """Download the file from the OMIQ dataset to the local scratch path."""
        self._api.download_file(
            dataset_id=self._dataset_id,
            file_id=self.file_id,
            filepath=self._scratch_path,
        )

    def _download_file_from_artifacts(self) -> None:
        """Download file from workflow artifacts to the local scratch path."""
        task_id = self._get_task_id_for_artifact(self.uuri.fragment)
        self._api.download_artifact(
            workflow_id=self.uuri.get_container_name(),
            task_id=task_id,
            artifact_name=self.uuri.fragment,
            filepath=self._scratch_path,
        )

    def _download_file_from_workflow(self) -> None:
        """Download a JSON file containing the OMIQ workflow."""
        dict_workflow = {"dataset": self._dataset_id, "workflow": self._workflow}
        with self._scratch_path / (
            "workflow_" + self._workflow_id + ".omiq_gfile"
        ).open("w") as gfile:
            json.dump(dict_workflow, gfile, indent=4)

    def _get_task_id_for_artifact(self, filename: str) -> str:
        """Get the task ID associated with the given artifact filename.

        Args:
            filename: The artifact filename to look up.

        Returns:
            The associated task ID.
        """
        return next(
            i["taskId"]
            for i in self._workflow.get("taskArtifacts", [])
            if i["file"] == filename
        )

    def _handle_file_not_found(self) -> None:
        """Handle the case when a file is not found in the workflow.

        Raises:
            FileNotFoundError: If the file or artifact is not found.
        """
        if self._corresponding_fcs_filename is None:
            f = self.uuri.fragment
        else:
            f = self._corresponding_fcs_filename
        msg = (
            f"file: ({f}) does not exist in workflow: {self.uuri.get_container_name()}"
        )
        raise FileNotFoundError(msg)

    @property
    def file_id(self) -> int:
        """Get the OMIQ file ID for the referenced file.

        Returns:
            The file ID as an integer.
        """
        tags = self.get_remote_tags()
        return tags["id"]

    @property
    def features(self) -> dict:
        """Get the OMIQ features metadata for the referenced file.

        Returns:
            Dictionary of feature metadata.
        """
        tags = self.get_remote_tags()
        return tags["features"]

    def _list_files_in_dataset(self) -> list:
        """List all files in the associated OMIQ dataset.

        Returns:
            List of file dictionaries.
        """
        return self._api.list_files_in_dataset(self._dataset_id)

    def _list_artifacts(self) -> list:
        """List all artifact filenames in the associated workflow.

        Returns:
            List of artifact file names.
        """
        return [i["file"] for i in self._workflow.get("taskArtifacts", [])]

    def list_container_items(
        self,
        pattern: str | None = None,
        full_string: bool = False,
    ) -> list:
        """Get all objects (files and artifacts) in the workflow or dataset.

        Args:
            pattern: Optional regex pattern to filter object names.
            full_string: Whether to return the list with full strings or just fragments.

        Returns:
            List of object names matching the filter.
        """
            container_objects = self.add_storage_uri_to_container_items(
                [file["displayName"] for file in self._list_files_in_dataset()],
            )
            container_objects += self.add_storage_uri_to_container_items(
                list(self._list_artifacts()),
            )
        else:
            logger.warning(
                "DeprecationWarning: list_container_items with full_string=False will be deprecated soon, use full_string=True instead.",
            )
            container_objects = [
                file["displayName"] for file in self._list_files_in_dataset()
            ]
            container_objects.extend(file for file in self._list_artifacts())
        if pattern is not None:
            container_objects = [
                name
                for name in container_objects
                if re.search(pattern, name) is not None
            ]
        return container_objects

    def remote_object_exists(self) -> bool:
        """Check if the object exists in the OMIQ container.

        Returns:
            True if the file or artifact exists, False otherwise.
        """
        return (
            self.uuri.fragment in self.list_container_items()
            or self._corresponding_fcs_filename in self._list_artifacts()
        )