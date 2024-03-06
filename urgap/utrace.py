
import copy
import datetime
import logging
import zlib
from base64 import b64encode
from collections import defaultdict as ddict



class UTrace:


    """

    def __init__(
        self,
        """Construct a new UTrace instance.

        Args:
            input_files: UFileList of (unfiltered) UFiles.
            unode_meta: UNode meta information dictionary.
            umeta_io: UMeta interface to use.
            output_files: Output files as UFileList.
        """
        self._output_base_storage_uri = None
        self._output_files_stem = None
        self._remote_output_files = None
        self.rerun_reasons = None
        self.unode_meta = self._init_unode_meta(unode_meta)

        self.urun_dict = self._init_urun_dict(urun_dict)
        if input_files is None:

        if output_files is None:
            self.populate_minimal_output_file_list()
            self.evaluate_retain_uftype()
        else:
            self.output_files = output_files

    @property
    def remote_output_files(self) -> dict:

        """
        if self._remote_output_files is None:
            self._remote_output_files = self._query_remote_by_uftype()
        return self._remote_output_files

        else:
        return urun_dict

        input_files = input_files.filter(
            input_uftypes=self.unode_meta["input_uftypes"],
            additional_filters=self.urun_dict.unode_parameters["additional_filters"],
        )
        if input_files is None:

        if len(input_files) == 0:
        return input_files

        if unode_meta is None:
        return copy.deepcopy(unode_meta)

        return

    @classmethod

        Args:
            umeta_dict: Dict containing umeta information.
        """

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

    @property

        input_storage_base_uris = set(self.input_files.get_storage_base_uris())
        params_storage_base_uri = self.urun_dict.unode_parameters["storage_base_uri"]
        if params_storage_base_uri is not None:
            output_storage_uri = params_storage_base_uri
        else:
        return output_storage_uri

    def determine_output_files_stem(self) -> os.PathLike:
        """Determine the root folder for output files.

        Returns:
        """
        object_folder = self._generate_top_level_folder_name(
            skip_data_versioning=self.urun_dict.unode_parameters[
                "skip_data_versioning"
            ],
        )

        if self.urun_dict.unode_parameters["prefix"] is not None:
            )

        if self.urun_dict.unode_parameters["override_folder_creation"] is True:
        else:
        return new_fragment

        self,
        if run_folder_name is None:
        else:
            top_level_folder = run_folder_name
        if skip_data_versioning is False:
        return top_level_folder

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
                self.unode_meta["output_uftypes"][i_uftype] = self.unode_meta[
                    "output_uftypes"
                ].pop(o_uftype)
                new_output_file_list = []
                for ofile in self.output_files:
                        uri=ofile.as_uri(
                    )
                    uf.tags.update({"uftype": i_uftype})
                    new_output_file_list.append(uf)

        uris = []
        for ouftype, mdict in self.unode_meta["output_uftypes"].items():
            if mdict["min"] == 0:
                continue
            if mdict["min"] == mdict["max"]:
                for n in range(1, mdict["max"] + 1):
                    uri = self.get_output_file_uri(
                        uftype=ouftype,
                        n=n,
                        max_n=mdict["max"],
                    )
                    uris.append(uri)
            elif mdict["max"] == -1:
                uri = self.get_output_file_uri(
                    uftype=ouftype,
                    n=1,
                    max_n="N",
                )
                uris.append(uri)
            elif mdict["min"] < mdict["max"]:
                uri = self.get_output_file_uri(
                    uftype=ouftype,
                    n=1,
                    max_n="N",
                )
                uris.append(uri)
            else:
        uris = [uri for uri in uris if uri is not None]

    def get_output_file_uri(
        self,
        uftype: str,

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
        if safe_to_create:
            uri = f"{self.output_base_storage_uri}?uftype={uftype}#{self.output_files_stem}_{n}_of_{max_n}{uftype}"
        else:
            uri = None
        return uri

    def extend_output_files_by_uftype(
        self,
        uftype: str,

        Args:
            n: Current number of files matching uftype.
            max_n: Max number of files matching uftype or "N" for an unspecified number.
        """

        remote_ofiles = ddict(list)
        if len(self.output_files) != 0:
            _ufile = self.output_files[0]
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



        Args:
        """

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


    @classmethod
    def load_from_umeta(
        cls,

        Args:
            umeta_io: UMeta interface to be used.

        Returns:
        """