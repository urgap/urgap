import datetime
import logging
from collections import defaultdict as ddict


class UTrace:


    """

    def __init__(
        self,
        """Construct a new UTrace instance.

        Args:
        """
        self._output_base_storage_uri = None
        self._output_files_stem = None
        self._remote_output_files = None
        self.rerun_reasons = None
        self.unode_meta = self._init_unode_meta(unode_meta)

        self.urun_dict = self._init_urun_dict(urun_dict)
        if input_files is None:

        if output_files is None:
            self.evaluate_retain_uftype()
        else:
            self.output_files = output_files

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

    @property
        if self._output_base_storage_uri is None:
            self._output_base_storage_uri = self._set_output_storage_uri()
        return self._output_base_storage_uri

    @property
        if self._output_files_stem is None:
            self._output_files_stem = self.determine_output_files_stem()
        return self._output_files_stem

    @property

        Returns:
        """

    @property
        return self.urun_dict.wid

    @property
        return self.output_files_stem

    @property

        Returns:
        """

    @property

        Returns:
        """

    @property

        input_storage_base_uris = set(self.input_files.get_storage_base_uris())
        params_storage_base_uri = self.urun_dict.unode_parameters["storage_base_uri"]
        if params_storage_base_uri is not None:
            output_storage_uri = params_storage_base_uri
        else:
        return output_storage_uri

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
                    new_output_file_list.append(uf)

        for ouftype, mdict in self.unode_meta["output_uftypes"].items():
            if mdict["min"] == 0:
                continue
            if mdict["min"] == mdict["max"]:
                for n in range(1, mdict["max"] + 1):
                        uftype=ouftype,
                        n=n,
                        max_n=mdict["max"],
                    )
            elif mdict["max"] == -1:
                    uftype=ouftype,
                    n=1,
                    max_n="N",
                )
            elif mdict["min"] < mdict["max"]:
                    uftype=ouftype,
                    n=1,
                    max_n="N",
                )
            else:


        Args:
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


        Returns:
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

        """Get list of input files in URunDict.

        Returns:
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
        else:



    @classmethod

        Args:

        Returns:
        """