from collections.abc import Iterable



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

        Returns:
        """


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


        Args:
        """
        self._eval_if_item_is_of_correct_type(item)
        super().insert(i, item)


        Returns:
        """

        kosha = False
            kosha = True
        if kosha is False:



        Raises:
        """
        already_seen_objects = set()
            else:
                flat_list.append(entry)


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


        Args:

        Returns:
        """
        return self.get_indices_matching_tag(tag="uftype", search_value=uftype)


        Args:

        Returns:
        """
        indices = []
        return indices


        Returns:
        """
        return {uftype: self.get_indices_by_uftype(uftype) for uftype in all_uftypes}


        Returns:
        """
        return {
            uftype: self.get_path_objects_by_uftype(uftype) for uftype in all_uftypes
        }


        Args:

        Returns:
        """
        idxs = self.get_indices_by_uftype(uftype)
        return [self[i].path for i in idxs]

        dynamic_index_groups = {}
        for uftype, idx_list in self.get_index_groups_by_uftypes().items():
            if self[idx_list[0]].is_borg:
                dynamic_index_groups[uftype] = idx_list
                for i in idx_list:
        return dynamic_index_groups


        Args:

        Returns:
        """
        needs_quantifier = False
        safe_to_create_new_file = False
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



        Returns:
        """
        return [x.as_storage_base_uri() for x in self]


        Args:

        Returns:
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
        """
        if isinstance(uftype_list, list) is False:
            )
            raise TypeError

        indices = []
        for key, value in self.get_index_groups_by_uftypes().items():
            if key in uftype_list:
                indices.extend(value)


    @classmethod


        """