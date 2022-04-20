from collections.abc import Iterable



class UFileList(UserList):

    """

        super().__init__(initlist=initlist)
        for item in self.data:
            self._eval_if_item_is_of_correct_type(item)
        self._output_definitions = None
        self.wid = None

    @property

        self._eval_if_item_is_of_correct_type(item)
        super().__setitem__(i, item)

        self._eval_if_item_is_of_correct_type(other)
        return super().__add__(other)

        self._eval_if_item_is_of_correct_type(other)
        return super().__radd__(other)

        self._eval_if_item_is_of_correct_type(other)
        return super().__iadd__(other)

        self._eval_if_item_is_of_correct_type(item)
        super().append(item)

        self._eval_if_item_is_of_correct_type(item)
        super().insert(i, item)


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
        if additional_filters is not None:
            for k, v_dict in additional_filters.items():

        ufile_classes = ddict(list)
        for ufile in self.create_flat_and_non_redundant_list():
            )


        for file_data_type, ufile_sublist in ufile_classes.items():
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


        Args:

        Returns:
        """
        indices = []
        return indices


        Returns:
        """


        Returns:
        """


        Args:

        Returns:
        """
        return [self[i].path for i in idxs]


        Args:

        Returns:
        """
        safe_to_create_new_file = False
                safe_to_create_new_file = True
        else:
            safe_to_create_new_file = True

        if safe_to_create_new_file is True:
            self.append(
            )
        return len(self) - 1


        return [x.as_storage_base_uri() for x in self]