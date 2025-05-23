
from __future__ import annotations

import collections.abc
import logging
import os
import subprocess

from collections import UserList, defaultdict, defaultdict as ddict
from collections.abc import Iterable
from pathlib import Path



class UFileList(UserList):

    Acts as a list with additional functionality to access and filter UFiles based on tags.
    """

    def __init__(self, initlist: list | None = None) -> None:
        """Initialize a UFileList.

        Args:
            initlist: Optional. List of UFile objects to initialize the list.
        """
        super().__init__(initlist=initlist)
        for item in self.data:
            self._eval_if_item_is_of_correct_type(item)
        self._output_definitions = None
        self.wid = None

    @property
    def all_remote_files_exist(self) -> bool:
        """Check if all files in the list exist at their remote locations.

        Returns:
            True if all remote files exist, otherwise False.
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
    ) -> None:
        """Insert an item at a specified index in the UFileList.

        Args:
            i: Index where the item should be set.
            item: Item to insert. Must comply with UFileList requirements.

        Raises:
            TypeError: If the item does not follow UFileList conventions.
        """
        self._eval_if_item_is_of_correct_type(item)
        super().__setitem__(i, item)

    def __add__(
    ) -> UFileList:
        """Concatenate another object to this UFileList.

        Args:
            other: Object to add. Can be UFile, UFileList, list, or tuple.

        Returns:
            New UFileList containing items from both lists.

        Raises:
            TypeError: If the object does not follow UFileList conventions.
        """
        self._eval_if_item_is_of_correct_type(other)
        return super().__add__(other)

    def __radd__(
    ) -> UFileList:
        """Concatenate this UFileList to another object.

        Args:
            other: Object to add. Can be UFile, UFileList, list, or tuple.

        Returns:
            New UFileList containing items from both lists.

        Raises:
            TypeError: If the object does not follow UFileList conventions.
        """
        self._eval_if_item_is_of_correct_type(other)
        return super().__radd__(other)

    def __iadd__(
    ) -> UFileList:
        """Extend this UFileList in-place with another object.

        Args:
            other: Object to add. Can be UFile, UFileList, list, or tuple.

        Returns:
            The updated UFileList.

        Raises:
            TypeError: If the object does not follow UFileList conventions.
        """
        self._eval_if_item_is_of_correct_type(other)
        return super().__iadd__(other)

        """Append an item to the UFileList if it follows conventions.

        Args:
            item: Item to append.

        Raises:
            TypeError: If the item does not follow UFileList conventions.
        """
        self._eval_if_item_is_of_correct_type(item)
        super().append(item)

    def insert(
        self,
        i: int,
    ) -> None:
        """Insert an item at a specified position if it follows conventions.

        Args:
            i: Index to insert the item at.
            item: Item to insert.

        Raises:
            TypeError: If the item does not follow UFileList conventions.
        """
        self._eval_if_item_is_of_correct_type(item)
        super().insert(i, item)

    def calculate_ucfs(self) -> collections.abc.Hashable:
        """Compute a combined hash for the UFiles in the list.

        The hash is based on the sorted UFile.ucfs values.

        Returns:
            A hash string representing the combined UFiles.
        """

    @property
    def id(self) -> collections.abc.Hashable:
        """Return a hash ID representing the UFileList.

        Returns:
            Hash string based on the UFiles in the list.
        """
        return self.calculate_ucfs()

    def _eval_if_item_is_of_correct_type(
    ) -> None:
        """Check if an item is suitable for inclusion in UFileList.

        Args:
            item: The item to check.

        Raises:
            TypeError: If the item does not follow UFileList conventions.
        """
        kosha = False
            kosha = True
        elif isinstance(item, list | tuple) is True:
        if kosha is False:
            msg = f"Item {item} cannot be used in UFileLists!"
            raise TypeError(msg)

    def create_flat_and_non_redundant_list(self) -> UFileList:
        """Flatten the UFileList to a single-level list without duplicates.

        Returns:
            A flat UFileList containing only unique UFiles.

        Raises:
            TypeError: If an item is not a UFile or if more than one level of nesting is found.
        """
        already_seen_objects = set()
        already_seen_objects, flat_list = self._get_flat_list(
            list_to_flatten=self.data,
            already_seen_objects=already_seen_objects,
            flat_list=flat_list,
        )
        return flat_list

    def _get_flat_list(

        Args:
            list_to_flatten: List to flatten.
            already_seen_objects: Set of already seen ucfs values.
            flat_list: List to append unique UFiles to.

        Returns:
            Tuple of already_seen_objects and the flat_list.

        Raises:
            TypeError: If non-UFile items or excessive nesting are encountered.
        """
        for entry in list_to_flatten:
            if entry is None:
                flat_list.append(None)
            elif isinstance(entry, Iterable):
                already_seen_objects, flat_list = self._get_flat_list(
                    list_to_flatten=entry,
                    already_seen_objects=already_seen_objects,
                    flat_list=flat_list,
                )
                msg = "Input files can only be list of UFiles and/or list of lists of Ufiles"
                raise TypeError(msg)
            elif entry.ucfs in already_seen_objects:
                continue
            else:
                already_seen_objects.add(entry.ucfs)
                flat_list.append(entry)
        return already_seen_objects, flat_list

    def filter(
        self,
        input_uftypes: dict | None = None,
        additional_filters: dict | None = None,
    ) -> UFileList:
        """Filter UFiles by input_uftypes and additional tag-based filters.

        Note:
            Input_uftypes in META_INFO dict of each wrapper has the following structure::

            META_INFO = {
                "input_uftypes": {
                        "min": 2,                # < minimum number of UFiles
                        "max": 4,                # < maximum number of UFiles
                    },
                }
            }
            Additional Filters can be passed during node.run() execution, enables more
            granular filtering on UFile tag bases, e.g. QC=bad, which has to be set on UFile
            level beforehand, e.g. manually::
                {
                            "tags": {"QC": "good"}, # < dict with tags the UFiles are checked against
                        }
                }

        Args:
            input_uftypes: Dictionary specifying required datatypes and file counts.
            additional_filters: Dictionary of additional tag-based filters.

        Returns:
            A UFileList if all criteria are met, otherwise None.

        Raises:
            ValueError: If number of filtered UFiles exceeds allowed maximum or is below minimum.
        """
        if input_uftypes is None:
            input_uftypes = {}
        if additional_filters is not None:
            for k, v_dict in additional_filters.items():
                if k not in input_uftypes:
                    input_uftypes[k] = {}
                input_uftypes[k].update(v_dict)

        ufile_classes = ddict(list)
        for ufile in self.create_flat_and_non_redundant_list():
            uftype = self.check_tags_on_ufile_for_uftype(
                input_uftypes=input_uftypes,
                ufile=ufile,
            )
            if uftype is not None:
                ufile_classes[uftype].append(ufile)
        return self.check_input_uftype_count(
            ufile_classes=ufile_classes,
            input_uftypes=input_uftypes,
        )

    def check_tags_on_ufile_for_uftype(
        self,
        input_uftypes: dict,
    ) -> str | None:
        """Check if a UFile has compatible uftype and the required tags.

        Args:
            input_uftypes: Dictionary of input uftypes from the wrapper.
            ufile: UFile object to check.

        Returns:
            The compatible uftype if found, else None.
        """
        mappable_uftypes = list(
        )
        if len(mappable_uftypes) == 0:
            msg = f"Filtered {ufile.uftype} UFile {ufile} - uftype is not compatible with wrapper uftype requirement"
            return None

        for uftype in mappable_uftypes:
            ufile_has_all_tags = True
            for k, v in input_uftypes[uftype].get("tags", {}).items():
                if ufile.tags.get(k, None) != v:
                    ufile_has_all_tags = False

            if ufile_has_all_tags:
                return uftype
            msg = f"Filtered {ufile.uftype} UFile {ufile} - missing tags"
            return None
        return None

    def check_input_uftype_count(
        self,
        ufile_classes: dict,
        input_uftypes: dict,
        """Check that the count of UFiles for each uftype is within allowed range.

        Args:
            ufile_classes: Dictionary of uftypes and their matched UFiles.
            input_uftypes: Dictionary of input uftypes from the wrapper.

        Returns:
            A filtered UFileList.

        Raises:
            ValueError: If there are too few or too many UFiles for a given uftype.
        """
        for file_data_type, ufile_sublist in ufile_classes.items():
            min_number_required = input_uftypes[file_data_type].get("min", 1)
            max_number_allowed = input_uftypes[file_data_type].get("max", -1)
            if len(ufile_sublist) >= min_number_required:
                if max_number_allowed == -1 or len(ufile_sublist) <= max_number_allowed:
                    filtered_ufile_list += ufile_sublist
                else:
                    msg = (
                        f"Received {len(ufile_sublist)} files with datatype {file_data_type}"
                        f"but expected a maximum of {max_number_allowed}."
                    )
                    raise ValueError(msg)
            else:
                msg = (
                    f"Received only {len(ufile_sublist)} files with datatype {file_data_type}"
                    f"but expected a minimum of {min_number_required}"
                )
                raise ValueError(msg)
        return filtered_ufile_list

    def get_indices_by_uftype(self, uftype: str) -> list[int]:
        """Get indices of UFiles with the specified uftype.

        Args:
            uftype: Uftype to search for.

        Returns:
            List of indices where uftype matches.
        """
        return self.get_indices_matching_tag(tag="uftype", search_value=uftype)

    def get_indices_matching_tag(
        self,
        tag: str | None = None,
        search_value: str | None = None,
    ) -> list[int]:
        """Get indices of UFiles where a tag matches the given value.

        Args:
            tag: Tag key to check.
            search_value: Value to match.

        Returns:
            List of matching indices.
        """
        indices = []
        if tag is None:
            for idx, ufile in enumerate(self):
                if ufile is None:
                    indices.append(idx)
            return indices
        for idx, ufile in enumerate(self):
            if ufile is None:
                continue
            leafs_with_matching_tag = [
                ext
                )
            ]
            if (".any." in search_value) or search_value.endswith(".ANY"):
                leafs_with_matching_tag.append(search_value)
            if ufile.tags.get(tag, None) in leafs_with_matching_tag:
                indices.append(idx)
        return indices

    def get_index_groups_by_uftypes(self) -> dict:
        """Create a dictionary mapping uftypes to the indices of matching UFiles.

        Returns:
            Dictionary mapping uftype to list of indices.
        """
        all_uftypes = {ufile.uftype for ufile in self if ufile is not None}
        if None in self:
            all_uftypes.add(None)
        return {uftype: self.get_indices_by_uftype(uftype) for uftype in all_uftypes}

    def get_path_object_groups_by_uftypes(self) -> dict:
        """Create a dictionary mapping uftypes to Path objects of UFiles.

        Returns:
            Dictionary mapping uftype to list of Path objects.
        """
        all_uftypes = {ufile.uftype for ufile in self}
        return {
            uftype: self.get_path_objects_by_uftype(uftype) for uftype in all_uftypes
        }

    def get_path_objects_by_uftype(self, uftype: str) -> list:
        """Return a list of Path objects for UFiles of the given uftype.

        Args:
            uftype: Uftype to match.

        Returns:
            List of Path objects.
        """
        idxs = self.get_indices_by_uftype(uftype)
        return [self[i].path for i in idxs]

    def get_index_groups_by_tag(self, tag: str) -> dict:
        """Group indices by tag value for all UFiles in the list.

        Args:
            tag: Tag name to group by.

        Returns:
            Dictionary mapping tag values to index lists.
        """
        index_groups = defaultdict(list)
        for idx, ufile in enumerate(self):
            if ufile.tags.get(tag, None) is not None:
                index_groups[ufile.tags[tag]].append(idx)
        return dict(index_groups)

    def complete_file_counts(self) -> dict:
        """Update file names with quantifier for dynamically generated files.

        Returns:
            Dictionary of uftypes to index lists for dynamic files.
        """
        dynamic_index_groups = {}
        old_files = []
        for uftype, idx_list in self.get_index_groups_by_uftypes().items():
            if uftype is None:
                continue
            if self[idx_list[0]].is_borg:
                dynamic_index_groups[uftype] = idx_list
                for i in idx_list:
                    if "_of_N" in self[i].object_name:
                        new_object_name = self[i].object_name.replace(
                            "_of_N",
                            f"_of_{len(idx_list)}",
                        )
                        old_files.append(self[i].path)
                        self[i].rebase(uri=f"#{new_object_name}")
        for path in old_files:
            path.unlink(missing_ok=True)
        return dynamic_index_groups

    def number_of_uftypes(self) -> dict:
        """Count number of UFiles per uftype in the list.

        Returns:
            Dictionary mapping uftype to the count of UFiles.
        """
        numbers_by_uftype = self.get_index_groups_by_uftypes()
        for k, v in numbers_by_uftype.items():
            numbers_by_uftype[k] = len(v)
        return numbers_by_uftype

    def extend_by_uftype(self, uftype: str) -> int:
        """Extend the UFileList with a new UFile based on output definitions.

        Args:
            uftype: The uftype for the new UFile.

        Returns:
            The index of the newly created UFile.
        """
        needs_quantifier = False
        safe_to_create_new_file = False
        current_counts = self.number_of_uftypes()
        if uftype in self.output_definitions["uftypes"]:
            current_count = current_counts[uftype]
            if self.output_definitions["uftypes"][uftype].get(
            ) != self.output_definitions["uftypes"][uftype].get("max", -1):
                needs_quantifier = True
                safe_to_create_new_file = True
            elif current_count <= self.output_definitions["uftypes"][uftype]["max"]:
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
                    uri=f"{self.output_definitions['storage_base_uri']}?uftype={self.output_definitions['uftype']}"
                    f"#{self.output_definitions['output_file_stem']}_{counter}{uftype}",
            )
        return len(self) - 1

    def add_ufile(self, uri: str) -> None:
        """Append a UFile to the list using a UUri.

        Args:
            uri: UUri to use for creating the UFile.
        """

    def get_storage_base_uris(self) -> list:
        """Return storage base UUris for each UFile in the list.

        Returns:
            List of storage base UUris.
        """
        return [x.as_storage_base_uri() for x in self]

    def remove_uftypes(self, uftype_list: list) -> UFileList:
        """Remove UFiles with the specified uftypes from the list.

        Args:
            uftype_list: List of uftypes to remove.

        Returns:
            New UFileList without the specified uftypes.

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


    def keep_uftypes(self, uftype_list: list) -> UFileList:
        """Keep only UFiles with specified uftypes in the list.

        Args:
            uftype_list: List of uftypes to retain.

        Returns:
            New UFileList containing only the specified uftypes.

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
        uftype: str | None = None,
    ) -> UFileList:
        """Create a UFileList from a list of UUris.


        """
        import concurrent.futures

            if uftype is not None:
                uf.tags["uftype"] = uftype
            return uf

        with concurrent.futures.ThreadPoolExecutor(
        ) as executor:
            ufile_list = executor.map(_init_ufile, uri_list)
        ufl = UFileList(ufile_list)
            ufl.download_ufiles(number_of_threads=number_of_threads)
        return ufl

    @classmethod
    def from_folder(
        cls,
        folder: str | Path,
        uftype: str | None = None,
    ) -> UFileList:
        """Create a UFileList from files in a folder.

        Args:
            folder: Path to the folder.
            number_of_threads: Number of threads for parallel download.
            uftype: Uftype to assign to resulting UFiles.

        Returns:
            Initialized UFileList.
        """
        uri_list = [
            f"file://{folder}#{str(file).replace(f'{folder}/', '')}"
            for file in Path(folder).rglob("*")
            if (
                file.is_file()
                and file.name.startswith(".") is False
                and file.name.endswith(".tag") is False
            )
        ]
        return UFileList.from_uri_list(
            uri_list=sorted(uri_list),
            number_of_threads=number_of_threads,
            uftype=uftype,
        )

    def as_uri_list(self) -> list:
        """Get a list of UUris for the UFiles in this list.

        Returns:
            List of UUris.
        """
        return [u.as_uri() for u in self]

    def simplify_names(
        self,
        source_object_names: set,
        prefix: str | None = None,
        suffix: str | None = None,
        storage_base_uri: str | None = None,
    ) -> UFileList:
        """Copy and rename UFiles using UFile.simplify_name.

        Args:
            source_object_names: Set of intended object name stems.
            prefix: Prefix for new names.
            suffix: Suffix for new names.
            storage_base_uri: Optional. New base UUri for renamed files.

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

        """Download all UFiles in the UFileList in parallel.

        Args:
            number_of_threads: Number of parallel threads to use.
        """
        msg = f"Starting download of UFileList in parallel with {number_of_threads} threads."
            args_list=self,
            number_of_threads=number_of_threads,
        )

        """Upload all UFiles in the UFileList in parallel.

        Args:
            number_of_threads: Number of parallel threads to use.
        """
        msg = f"Starting upload of UFileList in parallel with {number_of_threads} threads."
            args_list=self,
            number_of_threads=number_of_threads,
        )

    def uncompress(self, destination: Path) -> None:
        """Uncompress all files in the UFileList to the specified destination.

        Args:
            destination: Path to the destination directory.
        """
        workdir = Path.cwd()
        Path.mkdir(destination, parents=True, exist_ok=True)
        os.chdir(destination)
        try:
            with subprocess.Popen(
            ) as tar_process:
                        tar_process.stdin.write(split_file.read())
            tar_process.stdin.close()
            tar_process.wait()
            if tar_process.returncode != 0:
                msg = f"Tar extraction failed with returncode: {tar_process.returncode}"
            else:
        finally:
            os.chdir(workdir)