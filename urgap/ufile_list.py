
import collections.abc
import logging
from collections import UserList, defaultdict, defaultdict as ddict
from collections.abc import Iterable
from pathlib import Path



class UFileList(UserList):

    """


        Args:
        """
        super().__init__(initlist=initlist)
        for item in self.data:
            self._eval_if_item_is_of_correct_type(item)
        self._output_definitions = None
        self.wid = None

    @property
    def all_remote_files_exist(self) -> bool:

        Returns:
        """
        r_value = True
        for uf in self:
            if uf.io.remote_object_exists() is False:
                r_value = False
                break
        return r_value

    def __setitem__(
        self,
        i: int,

        Args:
        """
        self._eval_if_item_is_of_correct_type(item)
        super().__setitem__(i, item)


        Args:
        """
        self._eval_if_item_is_of_correct_type(other)
        return super().__add__(other)


        Args:
        """
        self._eval_if_item_is_of_correct_type(other)
        return super().__radd__(other)


        Args:
        """
        self._eval_if_item_is_of_correct_type(other)
        return super().__iadd__(other)


        Args:
        """
        self._eval_if_item_is_of_correct_type(item)
        super().append(item)

    def insert(
        self,
        i: int,

        Args:
        """
        self._eval_if_item_is_of_correct_type(item)
        super().insert(i, item)



        Returns:
        """

    @property
    def id(self) -> collections.abc.Hashable:

        Returns:
        """


        """
        kosha = False
            kosha = True
        if kosha is False:



        Raises:
        """
        already_seen_objects = set()
        already_seen_objects, flat_list = self._get_flat_list(
            list_to_flatten=self.data,
            already_seen_objects=already_seen_objects,
            flat_list=flat_list,
        )
        return flat_list

        for entry in list_to_flatten:
            if entry is None:
                flat_list.append(None)
            elif isinstance(entry, Iterable):
                already_seen_objects, flat_list = self._get_flat_list(
                    list_to_flatten=entry,
                    already_seen_objects=already_seen_objects,
                    flat_list=flat_list,
                )
                continue
            else:
                flat_list.append(entry)
        return already_seen_objects, flat_list

    def filter(
        self,

        Args:

        Returns:
        """
        if input_uftypes is None:
            input_uftypes = {}
        if additional_filters is not None:
            for k, v_dict in additional_filters.items():
                    input_uftypes[k] = {}
                input_uftypes[k].update(v_dict)

        ufile_classes = ddict(list)
        for ufile in self.create_flat_and_non_redundant_list():
            )



        for file_data_type, ufile_sublist in ufile_classes.items():
            min_number_required = input_uftypes[file_data_type].get("min", 1)
            max_number_allowed = input_uftypes[file_data_type].get("max", -1)
            if len(ufile_sublist) >= min_number_required:
                if max_number_allowed == -1 or len(ufile_sublist) <= max_number_allowed:
                    filtered_ufile_list += ufile_sublist
                else:
                    )
            else:
                )
        return filtered_ufile_list

    def get_indices_by_uftype(self, uftype: str) -> list[int]:

        Args:

        Returns:
        """
        return self.get_indices_matching_tag(tag="uftype", search_value=uftype)

    def get_indices_matching_tag(
        self,
    ) -> list[int]:

        Args:
            search_value: Value to match.

        Returns:
        """
        indices = []
        if tag is None:
            for idx, ufile in enumerate(self):
                if ufile is None:
                    indices.append(idx)
        return indices

    def get_index_groups_by_uftypes(self) -> dict:

        Returns:
        """
        if None in self:
            all_uftypes.add(None)
        return {uftype: self.get_indices_by_uftype(uftype) for uftype in all_uftypes}

    def get_path_object_groups_by_uftypes(self) -> dict:

        Returns:
        """
        return {
            uftype: self.get_path_objects_by_uftype(uftype) for uftype in all_uftypes
        }

    def get_path_objects_by_uftype(self, uftype: str) -> list:

        Args:

        Returns:
        """
        idxs = self.get_indices_by_uftype(uftype)
        return [self[i].path for i in idxs]

    def get_index_groups_by_tag(self, tag: str) -> dict:

        Args:

        Returns:
        """
        index_groups = defaultdict(list)
        for idx, ufile in enumerate(self):
            if ufile.tags.get(tag, None) is not None:
                index_groups[ufile.tags[tag]].append(idx)
        return dict(index_groups)

    def complete_file_counts(self) -> dict:

        Returns:
        """
        dynamic_index_groups = {}
        for uftype, idx_list in self.get_index_groups_by_uftypes().items():
            if uftype is None:
                continue
            if self[idx_list[0]].is_borg:
                dynamic_index_groups[uftype] = idx_list
                for i in idx_list:
        return dynamic_index_groups

    def number_of_uftypes(self) -> dict:

        Returns:
        """
        numbers_by_uftype = self.get_index_groups_by_uftypes()
        for k, v in numbers_by_uftype.items():
            numbers_by_uftype[k] = len(v)
        return numbers_by_uftype

    def extend_by_uftype(self, uftype: str) -> int:

        Args:

        Returns:
        """
        needs_quantifier = False
        safe_to_create_new_file = False
        current_counts = self.number_of_uftypes()
            current_count = current_counts[uftype]
            if self.output_definitions["uftypes"][uftype].get(
            ) != self.output_definitions["uftypes"][uftype].get("max", -1):
                needs_quantifier = True
                safe_to_create_new_file = True
        else:
            current_count = 1
            safe_to_create_new_file = True

        if safe_to_create_new_file is True:
            if needs_quantifier is True:
                counter = str(current_count + 1) + "_of_N"
            else:
                counter = current_count
            self.append(
            )
        return len(self) - 1


        Args:
        """

    def get_storage_base_uris(self) -> list:

        Returns:
        """
        return [x.as_storage_base_uri() for x in self]


        Args:

        Returns:

        Raises:
            TypeError: If uftype_list is not a list.
        """
        if isinstance(uftype_list, list) is False:
            )
            raise TypeError

        indices = []
        for key, value in self.get_index_groups_by_uftypes().items():
            if key not in uftype_list:
                indices.extend(value)



        Args:

        Returns:

        Raises:
            TypeError: If uftype_list is not a list.
        """
        if isinstance(uftype_list, list) is False:
            )
            raise TypeError

        indices = []
        for key, value in self.get_index_groups_by_uftypes().items():
            if key in uftype_list:
                indices.extend(value)


    @classmethod
    def from_uri_list(
        cls,
        uri_list: list[str],


        """
    @classmethod
    def from_folder(

        Args:

        Returns:
            Initialized UFileList.
        """

        return [u.as_uri() for u in self]

    def simplify_names(
        self,
        source_object_names: set,

        Args:
            source_object_names: Set of intended object name stems.

        Returns:
            UFileList with simplified names.
        """
        for ufile in self:
            renamed_ufile_list.append(
                ufile.simplify_name(
                    source_object_names=source_object_names,
                    prefix=prefix,
                    suffix=suffix,
                    storage_base_uri=storage_base_uri,
            )
        return renamed_ufile_list