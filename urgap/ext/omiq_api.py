"""Description of the module."""

from __future__ import annotations

import base64
import json
import os
import shutil
import time

from typing import Dict, List

import requests

TIMEOUT = 10

__version__ = "1.10.3"


class Logger:
    """Logger.

    Description of the class.

    """

    def log(self, message):
        """Log.

        Parameters
        ----------
        message : type
            Description of message.

        Return:
        type
            Description of return value.

        """
        print(message)


class ProcessingStatus:
    """Enum class for remote processing status."""

    UNSET = "UNSET"
    FAILED = "FAILED"
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"

    @staticmethod
    def is_processing(ps: str) -> bool:
        """Is_processing.

        Parameters
        ----------
        ps : type
            Description of ps.

        Return:
        type
            Description of return value.

        """
        return ps != ProcessingStatus.FAILED and ps != ProcessingStatus.COMPLETE


class APIErr:
    """APIErr.

    Description of the class.

    """

    def __init__(
        self,
        method: str | None,
        reason: str,
        code: int,
        url: str,
        response_content: str,
        response: requests.Response | None,
    ):
        """Customize class for wrapping a failed HTTP request for reporting errors.The underlying requests.Response may be included, however this can potentially be None."""
        self.method = method
        self.reason = reason
        self.code = code
        self.url = url
        self.response_content = response_content
        self.response = response

    def __str__(self):
        """__str__.

        Return:
        type
            Description of return value.

        """
        return f"APIErr: Failed {self.method} request to {self.url}\nCode: {self.code}\nReason: {self.reason}\nResponse content: {self.response_content}"

    def is_dupe_login_err(self):
        """Is_dupe_login_err.

        Return:
        type
            Description of return value.

        """
        match_str = "There is a more recent login for this account"
        return match_str in self.response_content

    def is_sharing_perm_err(self):
        """Is_sharing_perm_err.

        Return:
        type
            Description of return value.

        """
        match_str = "You do not have permission"
        return match_str in self.response_content

    @classmethod
    def from_response(cls, response: requests.Response):
        """Construct for APIErr which accepts a requests.Response and extracts relevant information from it to construct an APIErr."""
        return cls(
            response.request.method,
            reason=response.reason,
            code=response.status_code,
            url=response.url,
            response_content=response.content.decode(),
            response=response,
        )


def print_token_expiration(token):
    """Print_token_expiration.

    Parameters
    ----------
    token : type
        Description of token.

    Return:
    type
        Description of return value.

    """
    t_exp = _get_token_expiration(token)
    t_exp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_exp))
    is_exp = _check_token_expired(token)
    if is_exp:
        t_exp_str += " (token is expired)"
    else:
        t_exp_str += " (token is not expired)"
    print(t_exp_str)


class API:
    """API.

    Description of the class.

    """

    def __init__(
        self,
        api_subdomain="api",
        auth_token="",
        secret_filepath="",
        logger: Logger = Logger(),
    ):
        """Create a new API instance for interacting with the OMIQ server.

        Args:
        api_subdomain: This is the special API subdomain. In the case of app.omiq.ai it is api. For
            single tenancy OMIQ deployments, it will be the name of your access subdomain.
            E.g., yourcompany.omiq.ai will be "yourcompany" as the api_subdomain.
        auth_token: If authenticating by passing an auth token directly, this is the authorization token
            generated on the profile page in OMIQ. It will expire and can only be renewed inside OMIQ.
            To check the expiration of a token, use the print_token_expiration() function.
        secret_filepath: If authenticating using a secret file, pass filepath for this file. The auth token
            will then be generated and saved as an attribute on this instance of API. If using this
            method of authentication, API will auto-renew the token when it's expired. This is useful for
            long-running processes and service accounts.
            Secrets can only be provided by Omiq staff. The contents should be a json object with keys
            "token" and "email". The token is length 42 as of the time of writing.
        logger: Any class that implements the function log(message), such as the Logger class provided by
            this package. If left default, it will use that default class and print to stdout. Provide your
            own implementation if you want more sophisticated logging.
        Returns: A new instance of API.
        """
        self.logger = logger
        if auth_token == "" and secret_filepath == "":
            raise Exception("Must provide one of auth_token or secret_filepath")
        if api_subdomain == "app":
            api_subdomain = "api"
        if api_subdomain != "api":
            api_subdomain = api_subdomain + "-api"
        protocol = "https"
        self._baseurl = f"{protocol}://{api_subdomain}.omiq.ai/api"
        self.token = auth_token
        self._secret_filepath = secret_filepath
        self._secret = None
        if secret_filepath != "":
            self._secret = _get_secret_from_file(secret_filepath)
        self._refresh_token()

    def _log(self, message):
        """_log.

        Parameters
        ----------
        message : type
            Description of message.

        Return:
        type
            Description of return value.

        """
        self.logger.log(message)

    def _refresh_token(self):
        """_refresh_token.

        Return:
        type
            Description of return value.

        """
        if self._secret is not None:
            self.token = self._get_token_from_secret(self._secret)
        if self.expired():
            m = "Auth token is expired. Please create a new instance of API with a new token. To have API handle automated token renewal, use secret based authentication."
            raise Exception(m)
        self._basehdrs = {"Authorization": f"Bearer {self.token}"}

    def _manage_req(self, url: str, method="GET", internal_key="", data=None):
        """_manage_req.

        Parameters
        ----------
        url : type
            Description of url.

        method : type
            Description of method.

        internal_key : type
            Description of internal_key.

        data : type
            Description of data.

        Return:
        type
            Description of return value.

        """
        backoff_sec = 5
        num_tries = 3
        for i in range(num_tries):
            time.sleep(i * backoff_sec)
            val, err = self._do_req(url, method, internal_key, data)
            if err is not None:
                if err.is_dupe_login_err() or err.is_sharing_perm_err():
                    raise Exception(err)
                self._log(
                    f"Got request error on try {i + 1}. Retrying. Error details: {err}",
                )
            else:
                return val
        raise Exception(
            f"Got request error after {num_tries} tries. Error details: {err}",
        )

    def _poll_longop(self, originalResponse: requests.Response, longOpId):
        """_poll_longop.

        Parameters
        ----------
        originalResponse : type
            Description of originalResponse.

        longOpId : type
            Description of longOpId.

        Return:
        type
            Description of return value.

        """
        self._log(
            f"Response indicates a long operation has started (ID {longOpId})... Polling for completion (every 3.5s)...",
        )
        longOpUrl = f"{self._baseurl}/longops/{longOpId}"
        while True:
            time.sleep(3.5)
            resp, err = self._do_req(longOpUrl)
            if err is not None:
                return None, err
            if len(resp) == 0:
                self._log("Longop still running, waiting...")
                continue
            if "val" in resp:
                if "error" in resp["val"]:
                    return None, APIErr(
                        originalResponse.request.method,
                        "Internal Server Error",
                        500,
                        originalResponse.request.url,
                        "Longop request (ID {}) returned error: {}".format(
                            longOpId,
                            resp["val"]["error"],
                        ),
                        None,
                    )
                return resp["val"], None
            raise Exception(
                "Invalid longop response detected. Please ensure your API wrapper is up-to-date, and contact support if issue persists",
            )

    def _do_req(self, url, method="GET", internal_key="", data=None):
        """_do_req.

        Parameters
        ----------
        url : type
            Description of url.

        method : type
            Description of method.

        internal_key : type
            Description of internal_key.

        data : type
            Description of data.

        Return:
        type
            Description of return value.

        """
        if self.expired():
            self._refresh_token()
        low_meth = method.lower()
        if low_meth == "get":
            response = requests.get(
                url,
                headers=self._basehdrs,
                params=data,
                timeout=TIMEOUT,
            )
        elif low_meth == "get_raw":
            response = requests.get(
                url,
                headers=self._basehdrs,
                stream=True,
                timeout=TIMEOUT,
            )
            if response.status_code != 200:
                err = APIErr.from_response(response)
                return None, err
            return response, None
        elif low_meth == "post":
            if data is None:
                raise Exception("data arg can't be empty for a POST request")
            response = requests.post(
                url,
                headers=self._basehdrs,
                json=data,
                timeout=TIMEOUT,
            )
        elif low_meth == "patch":
            if data is None:
                raise Exception("data arg can't be empty for a PATCH request")
            response = requests.patch(
                url,
                headers=self._basehdrs,
                json=data,
                timeout=TIMEOUT,
            )
        elif low_meth == "delete":
            response = requests.delete(url, headers=self._basehdrs, timeout=TIMEOUT)
        else:
            raise Exception(
                f"{method} is not a currently supported HTTP method for this function",
            )
        val, err = self._handle_response(response, internal_key)
        return val, err

    def _handle_response(self, response: requests.Response, internal_key=""):
        """Handle common response using this helper function.

        Args:
        response: The requests.response.
        internal_key: The string key name for a sub-object within the response to return. Many
            response objects from the API have a top level key that doesn't have a purpose in this context.

        Returns:
        tuple:
            1: val: The response from the server, usually a dict, or if internal_key is specified, the value at
            that key. Or None in the case of an error.
            2: err: APIError if the response indicates as such, or None if the response was success.
        """
        if response.status_code != 200:
            err = APIErr.from_response(response)
            return None, err
        resp_obj = response.json()
        if "longOpId" in resp_obj:
            resp_obj, err = self._poll_longop(response, resp_obj["longOpId"])
            if err is not None:
                return None, err
        if internal_key != "":
            return resp_obj[internal_key], None
        return resp_obj, None

    def _get_token_from_secret(self, secret: str):
        """Get a new auth token generated from the server using the secret parsed from a secret file. Secret is json object with keys "email" and "token"."""
        url = f"{self._baseurl}/auth/login"
        backoff_sec = 5
        num_tries = 3
        for i in range(num_tries):
            time.sleep(i * backoff_sec)
            resp = requests.post(url, json=secret, timeout=TIMEOUT)
            val, err = self._handle_response(resp, "jwt")
            if err is not None:
                self._log(
                    f"Got secret->token auth request error on try {i + 1}. Retrying. Error details: {err}",
                )
            else:
                return val
        raise Exception(
            f"Failed secret->token authentication request after {num_tries} tries. Latest error details: {err}",
        )

    def expired(self):
        """Check if the token for this API instance is expired.

        Remember that tokens are automatically renewed when using secret based authentication. In that
        case, you don't need to worry about checking for expiration. See also the print_token_expiration() function.

        Returns:
        bool: Whether or not the current auth token for this API object is expired.
        """
        return self.token == "" or _check_token_expired(self.token)

    def get_platform_config(self):
        """Get_platform_config.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/settings/config"
        return self._manage_req(url, "GET", "config")

    def get_user(self):
        """Get_user.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/user"
        return self._manage_req(url, "GET", "user")

    def set_user_prefs(self, prefs: dict):
        """Set_user_prefs.

        Parameters
        ----------
        prefs : type
            Description of prefs.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/user/setprefs"
        return self._manage_req(url, "POST", "user", data={"prefs": prefs})

    def search_users(self, query: str):
        """Search_users.

        Parameters
        ----------
        query : type
            Description of query.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/users/search?query={query}"
        return self._manage_req(url, "GET", "users")

    def respond_to_connection_request(self, user_id, response):
        """Respond_to_connection_request.

        Parameters
        ----------
        user_id : type
            Description of user_id.

        response : type
            Description of response.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/users/connection"
        return self._manage_req(
            url,
            "PATCH",
            "user",
            data={"requesterId": user_id, "connect": response},
        )

    def list_groups(self) -> List[Dict]:
        """List all the Groups available to this User."""
        url = "{}/groups".format(self._baseurl)
        return self._manage_req(url, "GET", "groups")

    def get_group_member_info(self, group_id: int) -> Dict[str, List[Dict]]:
        """List the user info of the users in the group.
        Result is an object with keys `users` and `extUsers`, the latter only as applicable.
        Each key entry has an array of user info objects.
        """
        url = "{}/group/{}/memberinfo".format(self._baseurl, group_id)
        return self._manage_req(url, "GET")

    def list_workflows(
        self,
        templates_only=False,
        incl_ds_name=False,
        incl_owner_info=False,
        ignore_deleted_ds=True,
        limit=0,
    ) -> list[dict]:
        """List all the Workflows available to this user.

        templates_only: Return only Templates, excluding normal Workflows.
        incl_ds_name: Add the Dataset name as an attribute of each returned Workflow.
        incl_owner_info: Add the Onwer information as an attribute of each returned Workflow. This is
        to avoid requiring the list_owners endpoint.
        ignore_deleted_ds: Exclude Workflows from Datasets that currently reside in the Trash.
        limit: If greater than 0, return only the N most recently updated Workflows.
        """
        url = f"{self._baseurl}/workflows"
        query_params = {
            "templatesOnly": templates_only,
            "includeDatasetName": incl_ds_name,
            "ignoreDeletedDatasets": ignore_deleted_ds,
            "includeOwner": incl_owner_info,
            "limit": limit,
        }
        return self._manage_req(url, "GET", "workflows", data=query_params)

    def list_datasets(self, incl_owner_info=False, limit=0) -> list[dict]:
        """List all the Datasets available to this user.

        incl_owner: Add the Onwer information as an attribute of each returned Workflow. This is
            to avoid requiring the list_owners endpoint.
        limit: If greater than 0, return only the N most recently updated Workflows.
        """
        url = f"{self._baseurl}/datasets"
        query_params = {"includeOwner": incl_owner_info, "limit": limit}
        return self._manage_req(url, "GET", "datasets", data=query_params)

    def get_dataset(self, dataset_id):
        """Get_dataset.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets/{dataset_id}"
        return self._manage_req(url, "GET", "dataset")

    def create_dataset(self, name="New dataset created from API") -> dict:
        """Create_dataset.

        Parameters
        ----------
        name : type
            Description of name.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets"
        return self._manage_req(url, "POST", "dataset", data={"displayName": name})

    def set_dataset_metadata_tags(self, dataset_id, tags_dict):
        """Set_dataset_metadata_tags.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        tags_dict : type
            Description of tags_dict.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets/{dataset_id}/setmetadata"
        return self._manage_req(url, "POST", "dataset", data={"metadata": tags_dict})

    def set_workflow_metadata_tags(
        self,
        workflow_id: int,
        tags: dict[str, str],
    ) -> dict:
        """Set_workflow_metadata_tags.

        Parameters
        ----------
        workflow_id : type
            Description of workflow_id.

        tags : type
            Description of tags.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/workflows/{workflow_id}/setmetadata"
        return self._manage_req(url, "POST", "config", data={"metadata": tags})

    def delete_dataset(self, dataset_id):
        """Delete_dataset.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets/{dataset_id}/delete"
        return self._manage_req(url, "POST", "dataset", data={"delete": True})

    def delete_dataset_force(self, dataset_id):
        """Delete_dataset_force.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets/{dataset_id}/forcedelete"
        return self._manage_req(url, "POST", "", data={})

    def list_files_in_dataset(self, dataset_id: int) -> list[dict]:
        """List_files_in_dataset.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets/{dataset_id}/files"
        return self._manage_req(url, "GET", "files")

    def get_file_from_dataset(self, dataset_id, file_id):
        """Get_file_from_dataset.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        file_id : type
            Description of file_id.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets/{dataset_id}/files/{file_id}"
        return self._manage_req(url, "GET")

    def set_files_metadata(self, dataset_id, files_to_md_dict) -> list[dict]:
        """Set_files_metadata.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        files_to_md_dict : type
            Description of files_to_md_dict.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets/{dataset_id}/setomiqmetadata"
        return self._manage_req(
            url,
            "POST",
            "files",
            data={"omiqMetadatas": files_to_md_dict},
        )

    def download_file(self, dataset_id, file_id, filepath, verbose=True):
        """Download_file.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        file_id : type
            Description of file_id.

        filepath : type
            Description of filepath.

        verbose : type
            Description of verbose.

        Return:
        type
            Description of return value.

        """
        t1 = time.time()
        url = self._get_file_url(dataset_id, file_id)
        self._get_url_save_to_disk(url, filepath)
        if verbose:
            self._log(
                f"Download file {os.path.basename(filepath)} took {int(time.time() - t1)} seconds",
            )

    def download_files(self, files, dir, overwrite=False, verbose=True):
        """Download_files.

        Parameters
        ----------
        files : type
            Description of files.

        dir : type
            Description of dir.

        overwrite : type
            Description of overwrite.

        verbose : type
            Description of verbose.

        Return:
        type
            Description of return value.

        """
        if not os.path.isdir(dir):
            raise Exception(f"{dir} is not a directory.")
        for fil in files:
            filpath = os.path.join(dir, fil["displayName"])
            if not overwrite and os.path.exists(filpath):
                continue
            self.download_file(fil["datasetId"], fil["id"], filpath, verbose)

    def export_data(
        self,
        dataset_id: int,
        file_id: int,
        feature_names: list[str],
        add_row_nums: bool,
        filter_ids: list[str],
        workflow: dict,
        from_task_id: int,
        filepath: str,
        fmt="CSV",
        filter_usage_mode="NAMECOL",
        drop_not_filtered=False,
        reverse_scaling=False,
        overwrite=False,
        verbose=True,
    ):
        """Export data and download it to disk for one file. CSV is the default format.

        @dataset_id is the dataset the file is in.
        @file_id is the file ID to export.
        @feature_names is the list of feature names to export.
        @add_row_nums is if a column of original row numbers should be added to the file.
        @filter_ids is the optional list of filter IDs to add a filterName column to the exported
        data. Filter IDs are the primary ID from the nodes in a gating tree. See `get_available_filters()`.
        @workflow is the Workflow object from the `get_workflow()` endpoint
        @from_task_id is the task ID from which the data should be exported. This will govern the
        nature of the exported data and availability of certain filters and features which are
        dictated by different tasks in the Workflow. The task ID can be any task and need not
        (and should not) be an Export Data task. That task type is meant to replace this API
        endpoint. If your Workflow already has a completed export data task, then the result
        should be downloaded with `download_artifact()`
        @filepath is the path (including filename) on disk to save it to.
        @reverse_scaling is whether or not the effect of scaling tasks should be reversed. This argument
        corresponds to the "Exported Data Units" option in the GUI, with a True argument
        representing the "Original/raw" option in the GUI. Note this argument only matters when
        there are scaling tasks upstream of @from_task_id in the Workflow.
        @fmt is the format of the exported file. 'CSV' or 'FCS'.
        @filter_usage_mode is, when @filter_ids are provided, the way in which each row's filter
        membership is indicated.
        For 'NAMECOL', a single filter identity column is added to the exported data which gives
        the full filter path name for each row. Keep in mind that a row can be in many filters
        simultaneously, but only one is named in the column. In such a case, OMIQ chooses the filter
        with the smallest count.
        For 'BOOLCOLS', a new column is added to the exported data file for every filter in
        @filter_ids. For each row and each column, a value of 0 or 1 is given. 0 means outside the
        filter, 1 means inside.
        @drop_not_filtered is "Drop rows not found in any selected filters" in the GUI. If True and if
        providing @filter_ids, OMIQ will drop any rows in the exported Data that do not fall into
        at least one of the provided filters. If False, the same rows would be labeled blank in
        the exported data.
        @overwrite is whether to overwrite the file if it already exists on disk. If false and the
        file does exist, it will throw an exception.
        @verbose logs timing information for both prepping the exported file and the time to download it.
        """
        if not overwrite and os.path.exists(filepath):
            raise Exception(f"overwrite=False and {filepath} already exists.")
        inst = {"taskId": from_task_id, "config": workflow, "filters": filter_ids}
        req_obj = {
            "datasetId": dataset_id,
            "fileIds": [file_id],
            "featureNames": feature_names,
            "addOrigRowIdx": add_row_nums,
            "reverseTransform": reverse_scaling,
            "format": fmt,
            "filterUsageMode": filter_usage_mode,
            "dropNotFiltered": drop_not_filtered,
            "instructions": inst,
        }
        t1 = time.time()
        url = f"{self._baseurl}/export/initiate"
        signed_url = self._manage_req(url, "POST", "url", data=req_obj)
        t2 = time.time()
        self._get_url_save_to_disk(signed_url, filepath)
        if verbose:
            t_export = int(t2 - t1)
            t_download = int(time.time() - t1)
            self._log(
                f"export data file {os.path.basename(filepath)} took {t_export}s and {t_download}s for download",
            )

    def _get_file_url(self, dataset_id, file_id):
        """_get_file_url.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        file_id : type
            Description of file_id.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets/{dataset_id}/files/{file_id}/download"
        return self._manage_req(url, "GET", "url")

    def delete_file_from_dataset(self, dataset_id, file_id):
        """Delete_file_from_dataset.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        file_id : type
            Description of file_id.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets/{dataset_id}/files/{file_id}"
        return self._manage_req(url, "DELETE")

    def upload_files_to_dataset(
        self,
        dataset_id,
        filepaths: list[str],
        verbose=True,
    ) -> list[dict]:
        """Upload_files_to_dataset.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        filepaths : type
            Description of filepaths.

        verbose : type
            Description of verbose.

        Return:
        type
            Description of return value.

        """
        if type(filepaths) is not list:
            raise Exception(
                f"filepaths must be type list but got type {type(filepaths)}",
            )
        registered_files = self.register_files_for_upload(dataset_id, filepaths)
        api_files: list[dict] = registered_files["files"]
        signed_urls: list[str] = registered_files["signedUrls"]
        ok_files = self.put_files_to_urls(filepaths, api_files, signed_urls, verbose)
        if not all(ok_files):
            bad_files = [f for idx, f in enumerate(filepaths) if not ok_files[idx]]
            raise Exception(f"File upload failed for these files: {bad_files}.")
        return api_files

    def register_files_for_upload(self, dataset_id, filepaths: list[str]):
        """Register_files_for_upload.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        filepaths : type
            Description of filepaths.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets/{dataset_id}/files"
        req_files = [_make_file_obj(dataset_id, x) for x in filepaths]
        post_data = {"datasetKey": dataset_id, "files": req_files}
        return self._manage_req(url, "POST", data=post_data)

    def put_files_to_urls(
        self,
        filepaths: list[str],
        files: list[dict],
        urls: list[str],
        verbose=True,
        retries=2,
        backoff_sec=8,
    ) -> list[bool]:
        """Put_files_to_urls.

        Parameters
        ----------
        filepaths : type
            Description of filepaths.

        files : type
            Description of files.

        urls : type
            Description of urls.

        verbose : type
            Description of verbose.

        retries : type
            Description of retries.

        backoff_sec : type
            Description of backoff_sec.

        Return:
        type
            Description of return value.

        """
        l1, l2, l3 = len(filepaths), len(files), len(urls)
        if l1 != l2 or l1 != l3:
            raise Exception(
                f"Got unequal lengths for array args: {l1}, {l2}, {l3}",
            )
        retries = max(retries, 0)
        backoff_sec = max(backoff_sec, 0)
        ok_files = [(False) for x in filepaths]
        for i, fil in enumerate(files):
            up_url = urls[i]
            filepath = filepaths[i]
            if os.path.basename(filepath) != fil["fileName"]:
                raise Exception(
                    f"""Expected same names but got different values. Check lists:
{filepaths}
{files}""",
                )
            filesize = os.path.getsize(filepath)
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Length": str(filesize),
            }
            with open(filepath, "rb") as fil_buff:
                num_tries = retries + 1
                for try_idx in range(num_tries):
                    if ok_files[i]:
                        break
                    time.sleep(try_idx * backoff_sec)
                    t1 = time.time()
                    if verbose:
                        self._log(
                            "Uploading {} to {}".format(
                                os.path.basename(filepath),
                                fil["datasetId"],
                            ),
                        )
                    response = requests.put(
                        up_url,
                        data=fil_buff,
                        headers=headers,
                        timeout=TIMEOUT * 2,
                    )
                    if verbose:
                        self._log(f"  took {int(time.time() - t1)} seconds")
                    if response.status_code != 200:
                        self._log(
                            f"  Got request error on try {try_idx + 1} out of {num_tries}. Error details: {APIErr.from_response(response)}",
                        )
                    else:
                        ok_files[i] = True
        return ok_files

    def get_workflow(self, workflow_id) -> dict:
        """Get_workflow.

        Parameters
        ----------
        workflow_id : type
            Description of workflow_id.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/workflows/{workflow_id}"
        return self._manage_req(url, "GET", "config")

    def get_workflow_settings(self, workflow_id):
        """Get_workflow_settings.

        Parameters
        ----------
        workflow_id : type
            Description of workflow_id.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/workflows/{workflow_id}/settings"
        return self._manage_req(url, "POST", "workflowSettings", {})

    def create_workflow(
        self,
        dataset_id,
        workflow_name,
        from_id=None,
        keep_computed_results=False,
    ) -> dict:
        """Create_workflow.

        Parameters
        ----------
        dataset_id : type
            Description of dataset_id.

        workflow_name : type
            Description of workflow_name.

        from_id : type
            Description of from_id.

        keep_computed_results : type
            Description of keep_computed_results.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/workflows"
        init = from_id is None or from_id == 0
        keep_comp = keep_computed_results and not init
        req_obj = {
            "datasetId": dataset_id,
            "name": workflow_name,
            "initialize": init,
            "fromId": from_id,
            "keepComputedResults": keep_comp,
        }
        return self._manage_req(url, "POST", "config", data=req_obj)

    def update_workflow(self, workflow):
        """Update_workflow.

        Parameters
        ----------
        workflow : type
            Description of workflow.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/workflows"
        return self._manage_req(url, "POST", data=workflow)

    def update_task(self, workflow_id: int, task: dict) -> dict:
        """Update/save this task within the given Workflow.

        This overwrites the current state
        of the task in OMIQ with the task argument as provided here.
        Returns the latest version of the whole Workflow including the changes to the given task.
        """
        url = f"{self._baseurl}/workflows/{workflow_id}/updateTask"
        payload = {"task": task, "overrideLock": False}
        return self._manage_req(url, "POST", "config", data=payload)

    def download_artifact(
        self,
        workflow_id: int,
        task_id: int,
        artifact_name: str,
        filepath: str,
        verbose=True,
    ):
        """Download_artifact.

        Parameters
        ----------
        workflow_id : type
            Description of workflow_id.

        task_id : type
            Description of task_id.

        artifact_name : type
            Description of artifact_name.

        filepath : type
            Description of filepath.

        verbose : type
            Description of verbose.

        Return:
        type
            Description of return value.

        """
        t1 = time.time()
        url = self._get_artifact_url(workflow_id, task_id, artifact_name)
        self._get_url_save_to_disk(url, filepath)
        if verbose:
            t_elapsed = int(time.time() - t1)
            self._log(
                f"Download file {os.path.basename(filepath)} took {t_elapsed} seconds",
            )

    def _get_url_save_to_disk(self, url: str, filepath: str):
        """GET/fetch the given url and save the contents to disk at filepath."""
        response = self._manage_req(url, "GET_RAW")
        with open(filepath, "wb") as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)

    def _get_artifact_url(self, workflow_id, task_id, artifact_name):
        """_get_artifact_url.

        Parameters
        ----------
        workflow_id : type
            Description of workflow_id.

        task_id : type
            Description of task_id.

        artifact_name : type
            Description of artifact_name.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/workflows/{workflow_id}/getArtifactUrl"
        req_obj = {"taskId": task_id, "file": artifact_name, "download": True}
        return self._manage_req(url, "POST", "url", data=req_obj)

    def get_policies_for_resource(self, resource_id, resource_type="DATASET"):
        """Get_policies_for_resource.

        Parameters
        ----------
        resource_id : type
            Description of resource_id.

        resource_type : type
            Description of resource_type.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/iam/policies?resourceType={resource_type}&resourceId={resource_id}"
        return self._manage_req(url, "GET", "policies")

    def list_dataset_owners(self) -> dict[int, dict]:
        """List_dataset_owners.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/datasets_ops/listowners"
        return self._manage_req(url, "GET", "owners")

    def list_workflow_owners(self) -> dict[int, dict]:
        """List_workflow_owners.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/workflows_ops/listowners"
        return self._manage_req(url, "GET", "owners")

    def share_resource(
        self,
        resource_id,
        resource_name,
        user_ids,
        group_ids,
        resource_type="DATASET",
        role="READER",
        message="",
        no_email=True,
    ):
        """Share_resource.

        Parameters
        ----------
        resource_id : type
            Description of resource_id.

        resource_name : type
            Description of resource_name.

        user_ids : type
            Description of user_ids.

        group_ids : type
            Description of group_ids.

        resource_type : type
            Description of resource_type.

        role : type
            Description of role.

        message : type
            Description of message.

        no_email : type
            Description of no_email.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/sharing"
        req_obj = {
            "resourceType": resource_type,
            "resourceId": resource_id,
            "resourceName": resource_name,
            "role": role,
            "userIds": user_ids,
            "groupIds": group_ids,
            "message": message,
            "noEmail": no_email,
        }
        return self._manage_req(url, "POST", "policies", data=req_obj)

    def change_resource_owner(
        self,
        resource_id,
        new_owner_id,
        owner_type,
        resource_type="DATASET",
    ):
        """Change_resource_owner.

        Parameters
        ----------
        resource_id : type
            Description of resource_id.

        new_owner_id : type
            Description of new_owner_id.

        owner_type : type
            Description of owner_type.

        resource_type : type
            Description of resource_type.

        Return:
        type
            Description of return value.

        """
        url = f"{self._baseurl}/iam/policies/changeowners"
        req_obj = {
            "resourceId": resource_id,
            "updatedOwnerId": new_owner_id,
            "updatedOwnerType": owner_type,
            "resourceType": resource_type,
        }
        return self._manage_req(url, "POST", "policy", data=req_obj)

    def list_transfers(self, dataset_id: int) -> list[dict]:
        """List the External Transfers done for this Dataset.

        Returns list of objects, each of which represents a transfer operation and has many
        attributes of information about the transfer.
        """
        url = f"{self._baseurl}/crosstenant/listtransfers?datasetid={dataset_id}"
        return self._manage_req(url, "GET", "transfers")


def get_available_filters(workflow: dict, from_task_id: int) -> list[str]:
    """Get available filter IDs in this Workflow object.

    @workflow is the Workflow object from the `get_workflow()` endpoint.
    @from_task_id, if > 0, is task ID from which to consider the available filters. It
        will look at this task and all upstream tasks in the branch. If <= 0, will look
        at the entire Workflow. If the from_task_id is not in the Workflow, an exception
        will be thrown.
    """
    tasks_with_filters = ["GatingTask", "GraphViewerTask"]
    tasks: list[dict] = workflow["tasks"]
    if from_task_id > 0:
        t = find_task_by_id(workflow, from_task_id)
        if t is None:
            raise Exception("task ID {} not found", from_task_id)
        tasks = []
        task_id = from_task_id
        task = find_task_by_id(workflow, task_id)
        while task is not None:
            tasks.append(task)
            task_id = task["parentId"]
            task = find_task_by_id(workflow, task_id)
    gtasks = [t for t in tasks if t["type"] in tasks_with_filters]
    filt_ids: list[str] = ["UNFILTERED"]
    for _, t in enumerate(gtasks):
        nodes: dict[str, dict] = t["gatingTree"]["nodes"]
        filt_ids.extend(nodes.keys())
    return filt_ids


def find_task_by_id(workflow: dict, task_id: int) -> dict:
    """Find a task by id in the given workflow, else returns None."""
    tasks: list[dict] = workflow["tasks"]
    for _, task in enumerate(tasks):
        if task["id"] == task_id:
            return task
    return None


def _get_secret_from_file(secret_filepath):
    """Parse the secret file from on disk. Throws exception if file is not found or does not have the expected data inside of it, as judged by looking at keys within the JSON file."""
    if not os.path.exists(secret_filepath):
        raise FileNotFoundError(secret_filepath)
    with open(secret_filepath) as f:
        secret = json.load(f)
        for key in ["token", "email"]:
            if secret.get(key) is None:
                raise Exception("Secret is missing required key entry: " + key)
    return secret


def _make_file_obj(dataset_id, filepath):
    """_make_file_obj.

    Parameters
    ----------
    dataset_id : type
        Description of dataset_id.

    filepath : type
        Description of filepath.

    Return:
    type
        Description of return value.

    """
    if not os.path.isfile(filepath):
        raise Exception(f"ERROR: given path {filepath} is NOT a file.")
    return {
        "displayName": os.path.basename(filepath),
        "fileName": os.path.basename(filepath),
        "contentType": "application/octet-stream",
        "datasetId": dataset_id,
    }


def _check_token_expired(token):
    """Return: bool: whether the auth token is expired."""
    exp = _get_token_expiration(token)
    return exp < time.time() - 30


def _get_token_expiration(token):
    """_get_token_expiration.

    Parameters
    ----------
    token : type
        Description of token.

    Return:
    type
        Description of return value.

    """
    payload = token.split(".")[1] + "======="
    pstring = base64.b64decode(payload)
    pobj = json.loads(pstring)
    return pobj.get("exp")
