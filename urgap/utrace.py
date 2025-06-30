
from __future__ import annotations

import copy
import datetime
import logging
import shutil
import zlib

from base64 import b64encode
from collections import defaultdict as ddict
from pathlib import Path


if TYPE_CHECKING:
    import os


class UTrace:

    Each unode.run creates a UTrace, which combines URun_dict, ufile_list, and unode.meta information.

    The trace initializes the umeta interface.
    """

    def __init__(
        self,
        unode_meta: dict | None = None,
        unode_version: str | None = None,
        umeta_io: str | None = None,
        history: dict | None = None,
    ) -> None:
        """Construct a new UTrace instance.

        Args:
            input_files: UFileList of (unfiltered) UFiles.
            unode_meta: UNode meta information dictionary.
            unode_version: UNode tag / version, introduced in u3.
            umeta_io: UMeta interface to use.
            output_files: Output files as UFileList.
            history: UTrace history information.
        """
        self._output_base_storage_uri = None
        self._output_files_stem = None
        self._remote_output_files = None
        self.rerun_reasons = None
        self.unode_meta = self._init_unode_meta(unode_meta)
        if unode_version is not None:
            self.unode_meta["unode_version"] = unode_version
        self.umeta_io = umeta_io
        self._umeta = None

        if history is not None:
            self.history = history

        self.urun_dict = self._init_urun_dict(urun_dict)
        if input_files is None:
        self.input_files = input_files

        if output_files is None:
            self.populate_minimal_output_file_list()
            self.evaluate_retain_uftype()
        else:
            self.output_files = output_files

    @property
        """Get umeta IO object.

        Returns:
        """
        if self._umeta is None:
        return self._umeta

    @property
    def remote_output_files(self) -> dict:
        """Get remote output files by uftype.

        Returns:
            Dictionary in the form {<uftype1>: [UFiles], ...}.
        """
        if self._remote_output_files is None:
            self._remote_output_files = self._query_remote_by_uftype()
        return self._remote_output_files

        if self.unode_meta.get("unode_version", None) is None:
            if urun_dict is None:
            else:
                urun_dict = copy.deepcopy(urun_dict)
            urun_dict.register_unode_meta_info(self.unode_meta)
        else:
            if urun_dict is None:
            else:
                wid = urun_dict.wid
                urun_dict["wid"] = wid
            urun_dict.register_unode_meta_info(self.unode_meta)
        return urun_dict

        """Filter a UFileList by required input uftypes.

        Args:
            input_files: Input UFileList.

        Returns:
            Filtered UFileList.

        Raises:
            OSError: If input_uftypes requirements are not met or the list is empty.
        """
        input_files = input_files.filter(
            input_uftypes=self.unode_meta["input_uftypes"],
            additional_filters=self.urun_dict.unode_parameters["additional_filters"],
        )
        if input_files is None:
            msg = "input_uftypes for node have not been met, maybe the wrong number/type of instances were provided?"
            raise OSError(msg)

        if len(input_files) == 0:
            msg = "Input list is empty ..."
            raise OSError(msg)
        return input_files

        if unode_meta is None:
        return copy.deepcopy(unode_meta)

    def _init_umeta(self) -> None:
        return

    @classmethod
    def init_from_umeta_entries(cls, umeta_dict: dict) -> None:
        """No-op method for compatibility.

        Args:
            umeta_dict: Dict containing umeta information.
        """

    def info(self) -> None:
        """Print runtime information for this UTrace instance to logging."""
        time_str = datetime.datetime.now().astimezone().strftime("%H:%M:%S - %d.%m.%Y")
        log_message += "|   ]\n"
        log_message += "| - output_files: [\n"
        log_message += "|   ]\n"
        log_message += f"+{'-' * 40}"


    @property
    def output_base_storage_uri(self) -> str:
        """Get the output base storage UUri.

        Returns:
            Output base storage UUri as a string.
        """
        if self._output_base_storage_uri is None:
            self._output_base_storage_uri = self._set_output_storage_uri()
        return self._output_base_storage_uri

    @property
    def output_files_stem(self) -> str:
        """Get the output file stem.

        Returns:
            Output file stem as a string.
        """
        if self._output_files_stem is None:
            self._output_files_stem = self.determine_output_files_stem()
        return self._output_files_stem

    @property
    def id(self) -> tuple:
        """Get the UTrace node exe id and wid.

        Returns:
        """

    @property
    def wid(self) -> str:

        Returns:
            Workflow ID as a string.
        """
        return self.urun_dict.wid

    @property
        """Get the output files stem (node exe id).

        Returns:
            Output files stem as a string.
        """
        return self.output_files_stem

    @property
    def was_skipped(self) -> bool:
        """Determine if run execution was skipped.

        Returns:
            True if the run was skipped, else False.
        """
        return self.umeta.io.get_execution_status(*self.id) == 0

    @property
    def was_run(self) -> bool:
        """Determine if run execution was executed.

        Returns:
            True if the run was executed, else False.
        """
        exeuction_result_time = self.umeta.io.get_execution_status(*self.id)
        return (exeuction_result_time is not None) and (exeuction_result_time > 0)

    @property
    def crashed(self) -> bool:
        """Determine if a run execution crashed.

        Returns:
            True if the run crashed, else False.
        """
        return self.umeta.io.get_execution_status(*self.id) is None

    @property
    def execution_time(self) -> float:
        """Return full execution time in seconds.

        Returns:
            Number of seconds for full execution time.
        """
        return self.umeta.io.get_execution_status(*self.id)

    def _set_output_storage_uri(self) -> str:
        input_storage_base_uris = set(self.input_files.get_storage_base_uris())
        params_storage_base_uri = self.urun_dict.unode_parameters["storage_base_uri"]
        if params_storage_base_uri is not None:
            output_storage_uri = params_storage_base_uri
        elif len(input_storage_base_uris) == 1:
            output_storage_uri = input_storage_base_uris.pop()
        else:
            msg = (
                "If UNode run is trigged with multiple remote locations, then "
                "storage_base_uri must be defined explicitly in UParameteres"
            )
            raise TypeError(msg)
        return output_storage_uri

    def determine_output_files_stem(self) -> os.PathLike:
        """Determine the root folder for output files.

        Returns:
            Output file stem as a path-like object.
        """
        object_folder = self._generate_top_level_folder_name(
            run_folder_name=self.urun_dict.unode_parameters["run_folder_name"],
            skip_data_versioning=self.urun_dict.unode_parameters[
                "skip_data_versioning"
            ],
        )

        input_sequence_ucfs = self.input_files.id
        if self.urun_dict.unode_parameters["prefix"] is not None:
            input_sequence_ucfs = (
                self.urun_dict.unode_parameters["prefix"] + input_sequence_ucfs
            )

        if self.urun_dict.unode_parameters["override_folder_creation"] is True:
            new_fragment = input_sequence_ucfs
        else:
            new_fragment = object_folder + "/" + input_sequence_ucfs
        return new_fragment

    def _generate_top_level_folder_name(
        self,
        skip_data_versioning: bool = False,
        run_folder_name: str | None = None,
    ) -> os.PathLike:
        """Generate the top-level folder name for output files.

        Args:
            skip_data_versioning: If True, skip data versioning.
            run_folder_name: Custom run folder name.

        Returns:
            Top-level folder name as a path-like object.
        """
        if run_folder_name is None:
            unode_id_win_compatible = self.unode_meta["unode_full_identifier"].replace(
                ":",
                "_",
            )
            top_level_folder = f"{unode_id_win_compatible}_w{self.unode_meta['wrapper_version']['major']}"
        else:
            top_level_folder = run_folder_name
        if skip_data_versioning is False:
            top_level_folder += "_" + self.urun_dict.rerun_params_hash
        return top_level_folder

    def evaluate_retain_uftype(self) -> None:
        """Check if it is possible to retain uftypes of input UFiles.

        If uftypes are unique across the inputs, output UFiles are assigned the same uftype
        if specified by UNode parameter.
        """
        output_files_uftype_counts = self.output_files.number_of_uftypes()
        input_files_uftype_counts = self.input_files.number_of_uftypes()
        if self.urun_dict.unode_parameters["retain_uftype"] is True:
            if (
                len(output_files_uftype_counts.keys()) != 1
                or len(input_files_uftype_counts.keys()) != 1
            ):
                    "Input/output uftypes are not unique. Cannot retain uftype.",
                )
            else:
                i_uftype = next(iter(input_files_uftype_counts.keys()))
                o_uftype = next(iter(output_files_uftype_counts.keys()))
                self.unode_meta["output_uftypes"][i_uftype] = self.unode_meta[
                    "output_uftypes"
                ].pop(o_uftype)
                new_output_file_list = []
                for ofile in self.output_files:
                        uri=ofile.as_uri(
                            fragment=ofile.object_name.replace(o_uftype, i_uftype),
                        ),
                    )
                    uf.tags.update({"uftype": i_uftype})
                    new_output_file_list.append(uf)
                msg = f"Changed output uftypes to {i_uftype}."

    def populate_minimal_output_file_list(self) -> None:
        """Initialize the minimum number of UFiles for each uftype based on UNode meta info."""
        uris = []
        for ouftype, mdict in self.unode_meta["output_uftypes"].items():
            if mdict["min"] == 0:
                msg = f"{ouftype} optional, init skipped."
                continue
            if mdict["min"] == mdict["max"]:
                msg = f"{ouftype} initialising {mdict['max']}."
                for n in range(1, mdict["max"] + 1):
                    uri = self.get_output_file_uri(
                        uftype=ouftype,
                        n=n,
                        max_n=mdict["max"],
                    )
                    uris.append(uri)
            elif mdict["max"] == -1:
                msg = f"{ouftype} unbound, initialised 1 of N."
                uri = self.get_output_file_uri(
                    uftype=ouftype,
                    n=1,
                    max_n="N",
                )
                uris.append(uri)
            elif mdict["min"] < mdict["max"]:
                msg = f"{ouftype} range of files, initialised 1 of N."
                uri = self.get_output_file_uri(
                    uftype=ouftype,
                    n=1,
                    max_n="N",
                )
                uris.append(uri)
            else:
                msg = f"{ouftype} - don't know what to do with {mdict}."
        uris = [uri for uri in uris if uri is not None]

    def get_output_file_uri(
        self,
        uftype: str,
        n: int | None = None,
        max_n: str | int = "N",
    ) -> str | None:
        """Compute the UUri for a new extended UFile in output UFiles.

        Args:
            n: Current number of files matching uftype.
            max_n: Max number of files matching uftype or "N" for an unspecified number.

        Returns:
            New UUri as a string or None if not creatable.
        """
        safe_to_create = True
        if n is None:
            current_n = self.output_files.number_of_uftypes().get(uftype, 0)
            n = current_n + 1
            if (
                n > self.unode_meta["output_uftypes"][uftype]["max"]
                and self.unode_meta["output_uftypes"][uftype]["max"] != -1
            ):
                safe_to_create = False
            if n == self.unode_meta["output_uftypes"][uftype]["max"]:
                msg = f"Could finalize counts on {uftype}, reached maximum."
        if safe_to_create:
            uri = f"{self.output_base_storage_uri}?uftype={uftype}#{self.output_files_stem}_{n}_of_{max_n}{uftype}"
        else:
            uri = None
        return uri

    def extend_output_files_by_uftype(
        self,
        uftype: str,
        n: int | None = None,
        max_n: str | int = "N",
        exact_n_to_extend_by: int = 1,
    ) -> None:
        """Extend the output UFileList with a new UFile for the specified uftype.

        Args:
            n: Current number of files matching uftype.
            max_n: Max number of files matching uftype or "N" for an unspecified number.
            exact_n_to_extend_by: Exact number of files matching uftype.
        """
        for _ in range(exact_n_to_extend_by):
            uri = self.get_output_file_uri(uftype=uftype, n=n, max_n=max_n)
            if uri is not None:
                self.output_files.add_ufile(
                    uri=uri,
                )

    def move_output_files(
        self,
        files: list,
        uftype: str,
        extend_len: int = 0,
        keep_original_name: bool = False,
    ) -> None:
        """Move the output file to the expected position.

        Args:
            files: Path to source files which have to be moved.
            uftype: Uftype to extend output files by.
            extend_len: Number of files to extend.
            keep_original_name: Whether to set the original_name tag for the UFile.
        """
        if extend_len != 0:
            self.extend_output_files_by_uftype(
                uftype=uftype,
                max_n=extend_len,
                exact_n_to_extend_by=extend_len,
            )
        args_list = [
            (src, dest, keep_original_name)
            for src, dest in zip(
                files,
                self.output_files.get_indices_by_uftype(uftype=uftype),
                strict=True,
            )
        ]
        else:
            number_of_threads = 8
            func=self._move_output_file,
            args_list=args_list,
            number_of_threads=number_of_threads,
        )

    def _move_output_file(
        self,
        file: str | Path,
        output_file_index: int,
        keep_original_name: bool = False,
    ) -> None:
        """Move the output file to the expected position.

        Args:
            file: Path to source file.
            output_file_index: Index position of the UFile in the output UFileList.
            keep_original_name: Whether to set the original_name tag for the UFile.
        """
        uf = self.output_files[output_file_index]
        shutil.move(src=file, dst=uf.path)
        if keep_original_name is True:
            uf.tags.update({"original_name": str(file)})

    def _query_remote_by_uftype(self) -> dict:
        """Query remote files by uftype.

        Returns:
            Dictionary of uftype to UFile list.
        """
        remote_ofiles = ddict(list)
        if len(self.output_files) != 0:
            _ufile = self.output_files[0]
            for uftype in self.unode_meta["output_uftypes"]:
                for remote_file in _ufile.io.list_container_items(
                ):
                    if remote_file.endswith(".tag"):
                        continue
                    )
                    remote_ofiles[uftype].append(ufile)
        return remote_ofiles

    def evaluate_if_rerun_is_required(self) -> list:
        """Evaluate if rerun is required and return reasons.

        Returns:
            List of reasons for rerun. If empty, no rerun is triggered.
        """
        reasons = []
        if self.urun_dict.unode_parameters["force"] is True:
            reasons.append("You used (the) Force!")
        else:
            for (
                uftype,
                idx_list,
            ) in self.output_files.get_index_groups_by_uftypes().items():
                first_idx = idx_list[0]
                if "1_of_N" in self.output_files[first_idx].object_name:
                    number_of_remote_objects = len(self.remote_output_files[uftype])
                    min_n = self.unode_meta["output_uftypes"][uftype]["min"]
                    if min_n > number_of_remote_objects:
                        reasons.append(
                            f"Not all dynamic files were written. Minimum {min_n}"
                            f" yet found only {number_of_remote_objects}",
                        )
                else:
                    for idx in idx_list:
                        if self.output_files[idx].io.remote_object_exists() is False:
                            reasons.append(
                                f"Not all expected output file of type {uftype} exist.",
                            )
                            break
                if len(reasons) > 0:
                    break

        self.rerun_reasons = reasons
        return reasons

    def set_start_time(self) -> None:
        """Set the start time stamp."""
        self.start_time = datetime.datetime.now().astimezone()

    def set_stop_time(self, skipped: bool = False, crashed: bool = False) -> None:
        """Set the stop time stamp.

        Args:
            skipped: Whether the run was skipped.
            crashed: Whether the run crashed during execution.
        """
        if skipped is True:
            self.duration_seconds = 0
        elif crashed is True:
            self.duration_seconds = None
        else:
            self.duration_seconds = (
                datetime.datetime.now().astimezone() - self.start_time
            ).total_seconds()

    def get_parent_files(self) -> list:
        """Get list of input files in URunDict.

        Returns:
            List of input files.
        """
        ilist = self.urun_dict.data.get("input_files", None)
        if ilist is None:
            ilist = []
        return ilist

    def get_parent_hashes(self) -> list:
        """Get hashes of input files in URunDict.

        Returns:
            List of hashes.
        """
        ilist = self.urun_dict.input_files
        if ilist is None:
            ilist = []
        return [ufile.hash for ufile in ilist]

    def fix_dynamic_output_file_names(self) -> None:
        """Fill in completed integer counts for all output UFiles.

        Operation is performed inplace.
        """
        if len(self.rerun_reasons) == 0:
        else:
            self.output_files.complete_file_counts()
        self.output_files = self.output_files.create_flat_and_non_redundant_list()

    def upload_output_files(self) -> None:
        """Upload all output UFiles in UTrace."""
        unique_parents = set()
        for ifile in self.input_files:
            unique_parents.update(ifile.parents)
            unique_parents.add(ifile.object_name)
        parents_str = ",".join(sorted(unique_parents))
        for ofile in self.output_files:
            if ofile is None:
                continue
            ofile.tags.update(parent_tag_dict)
            files_to_upload.append(ofile)
        files_to_upload.upload_ufiles()

    def save_umeta_information(self) -> None:
        """Save UMeta information for this trace."""
        for ufile in self.output_files:
            if ufile is None:
                continue
            self.umeta.save_rebased_file_to_ucfs_storage_location(ufile=ufile)
        self.umeta.save_utrace(self)

    @classmethod
    def load_from_umeta(
        cls,
        wid: str,
        storage_base_uri: str,
        umeta_io: str | None = None,
        """Retrieve a UTrace from any given node and WID using the specified UMeta interface.

        Args:
            storage_base_uri: Storage_base_uri to retrieve associated UTrace.
            umeta_io: UMeta interface to be used.

        Returns:
            UTrace object for the requested run.
        """
        return umeta.load_utrace(
            wid=wid,
            storage_base_uri=storage_base_uri,
        )

    def add_execution_record(self) -> None:
        """Add an execution record for this trace."""
        self.umeta.io.add_execution_record(
            uwid=uwid,
            start_time=self.start_time,
            duration=self.duration_seconds,
            user_dict=self.user_dict,
        )