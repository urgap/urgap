"""URunDict module of urgap."""

from __future__ import annotations

import copy
import json
import logging

from collections import UserDict
from typing import ParamSpec

import urgap

P = ParamSpec("P")
logger = logging.getLogger(__name__)


class URunDict(UserDict):
    """Bag of configuration and runtime information for Urgap pipeline nodes.

    This object is initialized by the user prior to pipeline execution.
    During node execution (`node.run()`), this object (or a copy) is used to
    store runtime metadata, input file list and output file list into umeta for
    future references.

    Ultimately a URunDict is passed into the wrapper. URunDict can only be
    initialized with a dict containing:
      - Parameters for wrapper execution.
      - unode_parameters for high level unode base class execution.

    As part of the initialization, a workflow id (wid) is issued.

    Although the underlying storage is a dict, it is recommended to use property
    accessors to ensure data consistency.

    Main properties:
      - parameters
      - unode_parameters
      - unode_rinfo
      - input_files
      - output_files
      - command_list
      - wid

    See class docstring for expected internal structure and available fields.

    Structure of the URunDict is:

    .. code-block:: python

        {
            "parameters": dict(),      # <-- parameters specific to the wrappers
                                        #     or wrapped executables. These will be
                                        #     translated and stored under `translations`


            "user_dict": dict(),       # <-- can be used to store user metadata,
                                        #     which can later be found in the umeta DB,
                                        #     using, e.g. the workflow id (WID)


            "unode_parameters": {      # <-- parameter specific to the UNode

                "additional_filters": None,     # additional filters to be used during
                                                # filtering of the input file. These filters
                                                # must have the same format as input_uftypes on
                                                # UFiles, e.g.
                                        # {
                                        #   ursgal.uftypes.test.TEST_FILE1: {
                                        #      #  ^--- Defining the data type
                                        #       "tags": {"QC": "good"},
                                        #      #  ^--- dict with tags the UFiles are checked against
                                        #   }
                                        # }

                "force": False,         # Whether execution is forced

                "override_folder_creation": False,   # Whether folder creation should be skipped
                                                    # Not sure if still used ...

                "prefix": None,         # If all objectname should get an additional prefix, e.g.
                                        # prefix  = "ROS1_" would yield object names such as
                # test_node_v1_<re_run_param_md5>/ROS1_<input_file_ids_md5>_0.test_file2

                "run_folder_name": None,        # overwrite folder name creation, normally
                                                # by node name and re-run param md5 so
                                                # object name would look like
                # <run_folder_name>_<re_run_param_md5>/<input_file_ids_md5>_0.test_file2

                "skip_data_versioning": False,  # overwrite folder name creation, normally
                                                # by node name and re-run param md5 so
                                                # object name would look like
                # test_node_v1/<input_file_ids_md5>_0.test_file2

                "skip_pre_checks": False,       # whether pre_checks are done or not
                                                # before node execution, e.g. if all
                                                # 3rd party installations are done

                "storage_base_uri": None,       # Storage base uri can be used to redefine
                                                # where the output files should be uploaded to
                                                # e.g. gcs://bucket_X

                "record_skipped_runs": False,   # deprecated - we will store all execution info

                "remove_temporary_files": False,   # whether temporary files produced by the wrapper
                                                    # will be deleted
                "retain_uftypes": False,   # whether output file uftypes should be retained regardless
                                           # wrapper definition

                "file_io_timeout": None    # In seconds, after which the ufile list will be re-initialized.
                                           # This is helpful if the IO backend will time out during
                                           # long processing of a unode. None will skip re-init.

                "remote_url": None,        # remote execution url, e.g. localhost. This requires
                                           # uctl upi_server (API) to be started on the remote host via
                                           # uctl upi_server.
                                           # Only wrappers that have api_port in UMETA can be executed remotely.
                                           # We introduce this mainly to bring resources from different
                                           # containers into localhost network, e.g. in a pod in k8s
                                           # None means execution is done in the unode module.

                "remote_execution_timeout": 7200, # How long should the run wait for
                                                  # remote excute to finish (in seconds)
                                                  # default 2h


                                                                               },

            # Additionally, the following entries will be created during runtime and cannot
            # be directly provided by the user

            "wid" : ursgal.wid.UWIDGenerator().generate_wid()
                                            # Workflow ID
                                            # Available via ursgal.uwid_obj.generate_wid()
                                            # format u_<adjective>-<noun>-<verb>-<adjective>-<noun>

            "input_files": None,           # Although unode.run is taking urun_dict and ufiles
                                            # as input, for the sake of convenience both are
                                            # combined and passed to the wrapper

            "output_files": None,          # Autogenerated based on unode_rinfo,
                                            # input files and parameters

            "unode_rinfo": {               # UNode run info dict,

                "command_list": [],        # build during wrapper execution

                "rerun_reasons": [],       # Reason why re-run was re-triggered

                "meta_info": {             # Partial copy of wrapper.UMETA_INFO
                                            # will be set by `self.register_unode_meta_info`
                                            # e.g.:

                    "utranslation_style": "ursgal_style_1"

                },
            }

            "translations": dict(),         # Translation of `parameters` using UParama lib
        }
    """

    def __init__(self, *args: dict, **kwargs: P.kwargs) -> None:
        """Create a new URunDict for storing node and workflow parameters.

        All parameters needed for execution should be stored here. The URunDict is
        passed along from node to node in the pipeline.

        Args:
            *args: Dict(s) used to initialize the run dict.
            **kwargs: Additional key-value pairs to initialize the run dict.
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
                if k2 not in self[k]:
                    self[k][k2] = v2

        for k, v in self._default_setup_that_cannot_be_set_by_user.items():
            self[k] = v

        if "wid" not in kwargs:
            self.assign_wid()
        self["version"] = urgap.__version__

    def _update_default_storage(self, storage_key: str, user_dict: dict) -> str:
        """Update internal storage defaults with user dictionary.

        Args:
            storage_key: Key to update (e.g. 'unode_parameters').
            user_dict: Dictionary of user parameters.

        Returns:
            The merged dictionary.
        """
        default_storage_parameters = copy.deepcopy(
            self._storage_requirements[storage_key],
        )
        default_storage_parameters.update(user_dict)
        return default_storage_parameters

    @property
    def wid(self) -> str:
        """Get workflow ID (wid).

        Returns:
            Workflow ID as a string, generated at initialization.
        """
        return self["wid"]

    @wid.setter
    def wid(self, wid: str) -> None:
        """Set workflow ID (wid).

        Args:
            wid: Workflow ID string to assign.

        Warning:
            Be sure what you are doing as this will affect data finding in umeta.
        """
        logger.warning("Modifying WID, be sure that you know what you are doing ...")
        self["wid"] = wid

    def assign_wid(self) -> None:
        """Assign a new workflow ID (wid) to the run dict."""
        self["wid"] = urgap.uwid_obj.generate_wid()

    def reassign_wid(self) -> None:
        """Assign a new workflow ID (wid) to the run dict (alias for assign_wid)."""
        self.assign_wid()

    @property
    def parameters(self) -> dict:
        """Get wrapper parameters.

        Returns:
            Dictionary of wrapper parameters.
        """
        return self.get("parameters", {})

    @parameters.setter
    def parameters(self, parameters: dict) -> None:
        """Set wrapper parameters.

        Args:
            parameters: Parameters to use in URunDict.
        """
        self["parameters"] = parameters

    @property
    def user_dict(self) -> dict:
        """Get workflow user dictionary.

        Returns:
            User dictionary, such as workflow ID and node execution ID.
        """
        return self.get("user_dict", {})

    @user_dict.setter
    def user_dict(self, user_dict: dict) -> None:
        """Set workflow user dictionary.

        Args:
            user_dict: Workflow user dictionary.
        """
        self["user_dict"] = user_dict

    @property
    def unode_parameters(self) -> dict:
        """Get unode execution parameters.

        Returns:
            Dictionary of unode parameters.
        """
        return self["unode_parameters"]

    @unode_parameters.setter
    def unode_parameters(self, unode_parameters: dict) -> None:
        """Set unode execution parameters.

        Args:
            unode_parameters: New parameters for unode execution.

        Raises:
            TypeError: If unode_parameters is not a dict.
        """
        if isinstance(unode_parameters, dict) is False:
            msg = "Unode parameters must be a dict!"
            raise TypeError(msg)

        self["unode_parameters"] = self._update_default_storage(
            "unode_parameters",
            unode_parameters,
        )

    @property
    def unode_rinfo(self) -> dict:
        """Get run information dictionary for the unode.

        Returns:
            Dictionary of unode run info (e.g. rerun reasons, command list).
        """
        return self["unode_rinfo"]

    @unode_rinfo.setter
    def unode_rinfo(self, unode_rinfo: dict) -> None:
        """Set unode run information dictionary.

        Args:
            unode_rinfo: Dictionary with run info for unode.

        Raises:
            TypeError: If unode_rinfo is not a dict.
        """
        if isinstance(unode_rinfo, dict) is False:
            msg = "Unode rinfo must be a dict!"
            raise TypeError(msg)
        self["unode_rinfo"] = self._update_default_storage("unode_rinfo", unode_rinfo)

    @property
    def meta_info(self) -> dict:
        """Get meta information dictionary for the unode.

        Returns:
            Dictionary of meta info for the wrapper/unode.
        """
        return self.unode_rinfo["meta_info"]

    @meta_info.setter
    def meta_info(self, meta_info: dict) -> None:
        """Set meta information for the wrapper/unode.

        Args:
            meta_info: Wrapper meta information dictionary.
        """
        self.unode_rinfo["meta_info"] = meta_info

    @property
    def input_files(self) -> urgap.UFileList:
        """Get input UFileList.

        Returns:
            List of input files as a UFileList.
        """
        return self.data["input_files"]

    @input_files.setter
    def input_files(self, input_files: urgap.UFileList) -> None:
        """Set input UFileList.

        Args:
            input_files: List of input files as a UFileList.

        Raises:
            TypeError: If input_files is not a UFileList.
        """
        if isinstance(input_files, urgap.UFileList) is False:
            msg = "Input files must be instance of UFileList"
            raise TypeError(msg)
        self.data["input_files"] = input_files

    @property
    def output_files(self) -> urgap.UFileList:
        """Get output UFileList.

        Returns:
            List of output files as a UFileList.
        """
        return self.data["output_files"]

    @output_files.setter
    def output_files(self, output_files: urgap.UFileList) -> None:
        """Set output UFileList.

        Args:
            output_files: List of output files as a UFileList.

        Raises:
            TypeError: If output_files is not a UFileList.
        """
        if isinstance(output_files, urgap.UFileList) is False:
            msg = "Output files must be instance of UFileList"
            raise TypeError(msg)
        self.data["output_files"] = output_files

    @property
    def command_list(self) -> list:
        """Get the command list to be executed.

        Returns:
            List of command arguments to be run (usually via subprocess).
        """
        return self.unode_rinfo["command_list"]

    @command_list.setter
    def command_list(self, command_list: list[str]) -> None:
        """Set the command list for execution.

        Args:
            command_list: List of command arguments.

        Raises:
            TypeError: If command_list is not a list.
        """
        if isinstance(command_list, list) is False:
            msg = "command_list must be instance of list"
            raise TypeError(msg)
        self.unode_rinfo["command_list"] = command_list

    @property
    def params_hash(self) -> str:
        """Hash of all UNode related parameters.

        Returns:
            Hash of all parameters as a hex string.
        """
        return self._calculate_hash_for_params(rerun_only=False)

    @property
    def rerun_params_hash(self) -> str:
        """Hash of rerun-triggering UNode parameters.

        Returns:
            Hash of rerun-triggering parameters as a hex string.
        """
        return self._calculate_hash_for_params(rerun_only=True)

    def _calculate_hash_for_params(self, rerun_only: bool = False) -> str:
        """Calculate a hash of parameter set.

        Args:
            rerun_only: If True, hash only those parameters that trigger rerun.

        Returns:
            Hash as a hex string.
        """
        umeta_info = self.unode_rinfo["meta_info"]
        unode_full_identifier = umeta_info["unode_full_identifier"]
        if rerun_only:
            no_rerun_params = set(umeta_info["parameters_not_triggering_rerun"])
        else:
            no_rerun_params = set()
        try:
            parameters = self.parameters[unode_full_identifier]
        except KeyError as e:
            msg = f"KeyError for {e}: Parameters have to be supplied under unode_full_identifier"
            logger.warning(msg)
            parameters = self.parameters
        param_set = sorted(
            [(k, v) for k, v in parameters.items() if k not in no_rerun_params],
        )
        tmp_json = json.dumps(
            param_set,
            cls=urgap.uconvert.JSONEncoder,
        )
        tmp_json = json.loads(tmp_json, cls=urgap.uconvert.JSONDecoder)
        sorted_json = json.dumps(
            tmp_json,
            sort_keys=True,
            cls=urgap.uconvert.JSONEncoder,
        )
        return urgap.ucore.calculate_string_hash(
            hashable_iterable=[sorted_json.encode("UTF-8")],
            hash_algorithm=urgap.config["hash_algorithm"],
        )

    def _generate_container_folder_name(
        self,
        skip_data_versioning: bool = False,
        run_folder_name: str | None = None,
    ) -> str:
        """Generate the container folder name for output data.

        Args:
            skip_data_versioning: Whether to skip versioning in folder name.
            run_folder_name: Optional custom run folder name.

        Returns:
            The generated container folder name.
        """
        if run_folder_name is None:
            container_folder_name = "{}_w{}".format(
                self.unode_rinfo["meta_info"]["name"],
                self.unode_rinfo["meta_info"]["wrapper_version"]["major"],
            )
        else:
            container_folder_name = run_folder_name

        if skip_data_versioning is False:
            container_folder_name += "_" + self.rerun_params_hash
        return container_folder_name

    def determine_output_files_stem(self, ufiles: urgap.UFileList = None) -> str:
        """Determine the root folder for output files.

        The output file stem is composed as: <object_folder>/<prefix><input_sequence_hash>.

        Args:
            ufiles: List of UFiles.

        Returns:
            Path to output file stem.
        """
        if ufiles is None:
            ufiles = self.input_files

        if ufiles is None or len(ufiles) == 0:
            msg = "Cannot determine output name based on empty ufile list"
            raise ValueError(msg)
        self.data["object_folder"] = self._generate_container_folder_name(
            skip_data_versioning=self.unode_parameters["skip_data_versioning"],
            run_folder_name=self.unode_parameters["run_folder_name"],
        )

        input_sequence_ucfss = ufiles.calculate_ucfs()
        if self.unode_parameters["prefix"] is not None:
            input_sequence_ucfss = (
                self.unode_parameters["prefix"] + input_sequence_ucfss
            )

        if self.unode_parameters["override_folder_creation"] is True:
            new_fragment = input_sequence_ucfss
        else:
            new_fragment = self.data["object_folder"] + "/" + input_sequence_ucfss
        return new_fragment

    def register_unode_meta_info(self, meta_info: dict) -> None:
        """Copy required information from meta_info into self.unode_rinfo["meta_info"].

        Args:
            meta_info: Meta info dictionary to copy from.
        """
        if meta_info.get("parameters_not_triggering_rerun") is None:
            meta_info["parameters_not_triggering_rerun"] = []
        self.data["unode_rinfo"]["meta_info"] = copy.deepcopy(meta_info)
