
from __future__ import annotations

import bz2
import copy
import gzip
import logging
import re
import shutil
import tarfile
import zipfile
import zlib
from base64 import b64decode
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from zipfile import ZipFile


class UFile:

    def __init__(
        self,

        Args:
        """
        self._local_copy = None
        self._io = None
        self._lineage_root_files = None
        self._lineage_graph = None
        self.was_downloaded_to_scratch = False
        self._tags = None

        self._io = None

    @property
    def tags(self) -> dict:

        Returns:
        """
        if self._tags is None:
            self._tags = self.io.get_remote_tags()
            if self._tags is None:
                self._tags = {}
        return self._tags

    @property
    def is_borg(self) -> bool:

    @property
    def is_part_of_collection(self) -> bool:

    @property
    def path(self) -> Path:


        Returns:
        """
        if self.io.local_object_exists() is True:
            remote_tags = self.io.get_remote_tags()
            if remote_tags is None:
                if len(non_standard_tags) > 0:
                        "Remote has no tags, thus the file is not downloaded again."
                    )
                download_file = False
                    " Will not download file anymore."
                )
                download_file = False
            else:
                    self.tags.update(
                        {
                    )
                    )
                    download_file = True

        if download_file is True:
            self.purge_local_file()
            self.io.download()
        return self.io.scratch_path

    def __repr__(self) -> str:

        Returns:
        """


        Args:

        Returns:
        """


        Args:

        Returns:
        """

    @property
    def object_name(self) -> str:

        Returns:
        """

    @property
    def simple_name(self) -> str:

        Returns:
        """
        object_name = self.object_name

    @property

        Returns:
        """


        Args:

        Returns:
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if re.match(r"^_(?!_)", k):
                setattr(result, k, None)
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    @property

        Returns:
        """
            self.tags.update(
            )

    @property
    def uftype(self) -> str:

        Returns:
        """
        uftype = self.tags.get("uftype", None)
        if uftype is None:
        return uftype

    def upload(
        self,
        overwrite: bool = True,
        verify: bool = False,
        retries: int = 3,

    @property

        Returns:
        """
        if self._io is None:
            self._io = self.init_io_class()
        return self._io

    @classmethod
        cls,
        path_object: Path,
        number_of_parents: int = 1,

        Args:

        Returns:
        """
        basefolder = path_object.parent.resolve()
        container_content = path_object.name
        for _ in range(number_of_parents):
            basefolder = basefolder.parent.resolve()

    def as_uri(
        self,
    ) -> str:

        Args:

        Returns:
        """
            )

    def as_storage_base_uri(self) -> str:

        Returns:
        """


        Returns:

        Raises:
        """
            )


        Returns:
        """

    def remote_object_exists(self) -> bool:
        return self.io.remote_object_exists()

    def recalculate_hashes(self, force_local: bool = False) -> None:

        Args:
        """
            else:


        Args:
        """
        parsed_uri = urlparse(uri)

            scheme=None if parsed_uri.scheme == "" else parsed_uri.scheme,
            netloc=None if parsed_uri.netloc == "" else parsed_uri.netloc,
            path=None if parsed_uri.path == "" else parsed_uri.path,
            fragment=None if parsed_uri.fragment == "" else parsed_uri.fragment,
        )
        self._io = None
        try:
        except (shutil.SameFileError, FileNotFoundError):

            self.upload(**kwargs)


        Args:

        Returns:
        """
            suffix = ".zip"
            new_path = self.path.with_suffix(self.path.suffix + suffix)
            with ZipFile(new_path, "w", zipfile.ZIP_DEFLATED) as file:
                file.write(self.path, arcname=self.path.name)

            suffix = ".gz"
            new_path = self.path.with_suffix(self.path.suffix + suffix)
                out_file.writelines(file)

            suffix = ".tar"
            new_path = self.path.with_suffix(self.path.suffix + suffix)
            with tarfile.open(new_path, mode="w:") as file:
                file.add(self.path, arcname=self.path.name)

        else:
            )

        return compressed_ufile


    def uncompress(
        self,
        recursive: bool = True,

        Args:

        Returns:
        """
        if compression_format is None:
        match compression_format:
            case "zip":
                with ZipFile(self.path, "r") as z_file:
                    z_file.extractall(path=temp_folder)
            case "gz":
                temp_folder.mkdir(parents=True, exist_ok=True)
                gz_output = temp_folder / self.path.stem
                try:
                    self._unpack_gz(gz_output=gz_output, encoding="utf-8")
                except UnicodeDecodeError:
                    self._unpack_gz(gz_output=gz_output, encoding="ISO-8859-1")
            case "tar":
                with tarfile.open(self.path, mode="r:") as tfile:
            case "split_tar":
                ).uncompress(temp_folder)
            case "bz2":
                temp_folder.mkdir(parents=True, exist_ok=True)
                with bz2.BZ2File(self.path) as bz_file:
                    file_names = [str(self.path.with_suffix("").name)]
                        shutil.copyfileobj(bz_file, f)
            case _:
                )
        if recursive is True:
                    )
                    try:
                        Path.unlink(uf.path)
                    except (FileExistsError, IsADirectoryError, NotADirectoryError):
                        )
                        to_be_removed = uf.path
                        uf.rebase(
                            uri=f"#{uf.object_name}.renamed",
                            upload=True,
                        )
                        uf.purge_local()

        self.io.create_container()

        self.io.remove_remote_object()

        self.purge_local_file()
        self.purge_local_tags()

            self.io.scratch_path.unlink()

        self._tags = None


    def identify_lineage_root_files(self, use_umeta: bool = True) -> list:

        Args:

        Returns:
        """
        if self._lineage_root_files is None:
            graph = self.create_lineage_graph(use_umeta=use_umeta)
            self._lineage_root_files = [
                node for node, in_degree in graph.in_degree() if in_degree == 0
            ]
        return self._lineage_root_files

    def create_lineage_graph(self, use_umeta: bool = True) -> nx.DiGraph:

        Args:

        Returns:
        """
        if self._lineage_graph is None:
            if use_umeta is True:
                graph = ur.graph
            else:
                graph = nx.DiGraph()
                graph = self._walk_via_objects(
                    graph=graph,
                    ufile=self,
                )
            self._lineage_graph = graph
        return self._lineage_graph

        graph.add_node(ufile.object_name)
        for parent in ufile.parents:
            graph.add_edge(
                parent,
                ufile.object_name,
                weight=4.7,
                arrow=True,
            )
            parent_uri = ufile.as_uri(fragment=parent, query="")
            parent_ufile.purge_local()
            graph = self._walk_via_objects(
                graph=graph,
                ufile=parent_ufile,
            )
        return graph

    @property
    def parents(self) -> list:

        Returns:
        """

    def simplify_name(
        self,
        source_object_names: set,

        Args:

        Returns:
        """
        matching_source = source_object_names.intersection(self.parents)
        if len(matching_source) != 1:
            return None
        simple_name = ""
        if prefix is not None:
            simple_name += prefix
        if suffix is not None:
            simple_name += suffix
        if storage_base_uri is None:
            self.rebase(uri=f"#{simple_name}", upload=True, overwrite=False)
        else:
            self.rebase(
            )
        return self