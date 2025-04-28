
from __future__ import annotations

import copy
import datetime
import logging
import zlib

from base64 import b64encode
from collections import defaultdict as ddict


if TYPE_CHECKING:
    import os


class UTrace:


    """

    def __init__(
        self,
        unode_meta: dict | None = None,
        unode_version: str | None = None,
        umeta_io: str | None = None,
    ) -> None:
        """Construct a new UTrace instance.

        Args:
            input_files: UFileList of (unfiltered) UFiles.
            unode_meta: UNode meta information dictionary.
            unode_version: UNode tag / version, introduced in u3.
            umeta_io: UMeta interface to use.
            output_files: Output files as UFileList.
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

        self.urun_dict = self._init_urun_dict(urun_dict)
        if input_files is None:
        self.input_files = input_files

        if output_files is None:
            self.populate_minimal_output_file_list()
            self.evaluate_retain_uftype()
        else:
            self.output_files = output_files

    @property

        Returns:
        """
        if self._umeta is None:
        return self._umeta

    @property
    def remote_output_files(self) -> dict:

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


        Args:

        Returns:
            Filtered UFileList.
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

        Args:
            umeta_dict: Dict containing umeta information.
        """

    def info(self) -> None:
        time_str = datetime.datetime.now().astimezone().strftime("%H:%M:%S - %d.%m.%Y")
        log_message += "|   ]\n"
        log_message += "| - output_files: [\n"
        log_message += "|   ]\n"
        log_message += f"+{'-' * 40}"


    @property
    def output_base_storage_uri(self) -> str:
        if self._output_base_storage_uri is None:
            self._output_base_storage_uri = self._set_output_storage_uri()
        return self._output_base_storage_uri

    @property
    def output_files_stem(self) -> str:
        if self._output_files_stem is None:
            self._output_files_stem = self.determine_output_files_stem()
        return self._output_files_stem

    @property
    def id(self) -> tuple:

        Returns:
        """

    @property
    def wid(self) -> str:
        return self.urun_dict.wid

    @property
        return self.output_files_stem

    @property
    def was_skipped(self) -> bool:

        Returns:
        """

    @property
    def was_run(self) -> bool:

        Returns:
        """
        return (exeuction_result_time is not None) and (exeuction_result_time > 0)

    @property
    def crashed(self) -> bool:

        Returns:
        """

    @property
    def execution_time(self) -> float:

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
        """
        object_folder = self._generate_top_level_folder_name(
            run_folder_name=self.urun_dict.unode_parameters["run_folder_name"],
            skip_data_versioning=self.urun_dict.unode_parameters[
                "skip_data_versioning"
            ],
        )

        if self.urun_dict.unode_parameters["prefix"] is not None:
            )

        if self.urun_dict.unode_parameters["override_folder_creation"] is True:
        else:
        return new_fragment

    def _generate_top_level_folder_name(
        self,
        skip_data_versioning: bool = False,
        run_folder_name: str | None = None,
    ) -> os.PathLike:
        if run_folder_name is None:
            unode_id_win_compatible = self.unode_meta["unode_full_identifier"].replace(
            )
            top_level_folder = f"{unode_id_win_compatible}_w{self.unode_meta['wrapper_version']['major']}"
        else:
            top_level_folder = run_folder_name
        if skip_data_versioning is False:
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
                    )
                    uf.tags.update({"uftype": i_uftype})
                    new_output_file_list.append(uf)
                msg = f"Changed output uftypes to {i_uftype}."

    def populate_minimal_output_file_list(self) -> None:
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

        Args:
            n: Current number of files matching uftype.
            max_n: Max number of files matching uftype or "N" for an unspecified number.

        Returns:
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
    ) -> None:

        Args:
            n: Current number of files matching uftype.
            max_n: Max number of files matching uftype or "N" for an unspecified number.
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
                        )
                else:
                    for idx in idx_list:
                        if self.output_files[idx].io.remote_object_exists() is False:
                            reasons.append(
                            )
                            break
                if len(reasons) > 0:
                    break

        self.rerun_reasons = reasons
        return reasons

    def set_start_time(self) -> None:
        self.start_time = datetime.datetime.now().astimezone()


        Args:
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


        Returns:
        """
        ilist = self.urun_dict.input_files
        if ilist is None:
            ilist = []

    def fix_dynamic_output_file_names(self) -> None:
        """Fill in completed integer counts for all output UFiles.

        Operation is performed inplace.
        """
        if len(self.rerun_reasons) == 0:
        else:
            self.output_files.complete_file_counts()
        self.output_files = self.output_files.create_flat_and_non_redundant_list()

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

    def save_umeta_information(self) -> None:
        self.umeta.save_utrace(self)

    @classmethod
    def load_from_umeta(
        cls,
        umeta_io: str | None = None,

        Args:
            umeta_io: UMeta interface to be used.

        Returns:
        """

        self.umeta.io.add_execution_record(
            uwid=uwid,
            start_time=self.start_time,
            duration=self.duration_seconds,
            user_dict=self.user_dict,
        )