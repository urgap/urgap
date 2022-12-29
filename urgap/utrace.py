import datetime
import logging
from collections import defaultdict as ddict


class UTrace:


    """

        self._output_base_storage_uri = None
        self._output_files_stem = None
        self.unode_meta = self._init_unode_meta(unode_meta)
        self.urun_dict = self._init_urun_dict(urun_dict)
        else:
        return urun_dict

            input_uftypes=self.unode_meta["input_uftypes"],
            additional_filters=self.urun_dict.unode_parameters["additional_filters"],
        )


        if unode_meta is None:
        return copy.deepcopy(unode_meta)

        return


    @property
        if self._output_base_storage_uri is None:
            self._output_base_storage_uri = self._set_output_storage_uri()
        return self._output_base_storage_uri

    @property
        if self._output_files_stem is None:
            self._output_files_stem = self.determine_output_files_stem()
        return self._output_files_stem

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

        output_files_uftype_counts = self.output_files.number_of_uftypes()
        input_files_uftype_counts = self.input_files.number_of_uftypes()
        if self.urun_dict.unode_parameters["retain_uftype"] is True:
            if (
                len(output_files_uftype_counts.keys()) != 1
            ):
                )
            else:

        for ouftype, mdict in self.unode_meta["output_uftypes"].items():
            if mdict["min"] == 0:
                        uftype=ouftype,
                        n=n,
                        max_n=mdict["max"],
                    )
            else:

        safe_to_create = True
            n = current_n + 1
                safe_to_create = False
        if safe_to_create:


        reasons = []
        if self.urun_dict.unode_parameters["force"] is True:
            reasons.append("You used (the) Force!")
        else:
                        )
                            reasons.append(
                            )
                            break
        return reasons



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

        else:

