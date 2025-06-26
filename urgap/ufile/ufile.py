
from __future__ import annotations

import bz2
import contextlib
import copy
import gzip
import hashlib
import logging
import re
import shutil
import tarfile
import zipfile
import zlib

from base64 import b64decode
from pathlib import Path
from typing import ParamSpec
from urllib.parse import urlparse, urlunparse
from zipfile import ZipFile

import networkx as nx


P = ParamSpec("P")


class UFile:

    def __init__(
        self,
        uri: str,
    ) -> None:
        """Create a new UFile instance.

        Args:
            uri: Full UUri to the file.
        """
        self.uri = uri
        self.format_uri()
        self._local_copy = None
        self._io = None
        self._lineage_root_files = None
        self._lineage_graph = None
        self.was_downloaded_to_scratch = False
        self._tags = None

            uri=self.uri,
        )
        self._io = None
        self._ucfs = None

    def format_uri(self) -> None:
        """Format the URI if storage_base_uri and ucfs combination was used to construct uri."""
        if "@" in self.uri:
            uri, ucfs_hash = self.uri.split("@")
                uri=uri,
                query=f"{hash_algorithm}={ucfs_hash}",
            )

    @property
    def tags(self) -> dict:
        """Get tags associated with this UFile.

        Returns:
            A dictionary of tags for this UFile, merged from remote and UUri query if present.
        """
        if self._tags is None:
            self._tags = self.io.get_remote_tags()
            if self._tags is None:
                self._tags = {}
            if len(self.uuri.query.keys()) > 0:
                self._tags.update(self.uuri.query)

        return self._tags

    @property
    def is_borg(self) -> bool:
        """Whether this file is part of a multifile (borg) collection.

        Returns:
            True if part of a collection, False otherwise.
        """
        return "_1_of_1" not in self.object_name and "_of_" in self.object_name

    @property
    def is_part_of_collection(self) -> bool:
        """Whether this file is part of a multifile collection.

        Returns:
            True if part of a collection, False otherwise.
        """
        return "_1_of_1" not in self.object_name and "_of_" in self.object_name

    @property
    def path(self) -> Path:
        """Path to the local scratch copy of this UFile.

        If not present locally or if hashes differ, downloads the remote file.

        Returns:
            Local file path.
        """
        download_file = True
        if self.io.local_object_exists() is True:
            download_file = False
            remote_tags = self.io.get_remote_tags()
            if remote_tags is None:
                non_standard_tags = (
                    set(self.tags.keys()) - hashlib.__dict__["algorithms_available"]
                )
                if len(non_standard_tags) > 0:
                        "Remote has no tags, thus the file is not downloaded again."
                        " Delete local explicitly UFile.purge_local_files() if needed.",
                    )
                download_file = False
                    "Remote has tag capability but hash was not set."
                    " Will not download file anymore."
                    " Delete local explicitly UFile.purge_local_files() if needed.",
                )
                download_file = False
            else:
                    self.tags.update(
                        {
                                "hash_algorithm"
                                self.io.scratch_path,
                            ),
                        },
                    )
                if self.tags.get(
                    None,
                        "Remote and local have different hash. Overwriting local",
                    )
                    download_file = True

        if download_file is True:
            self.purge_local_file()
            self.io.download()
        return self.io.scratch_path

    def __repr__(self) -> str:
        """Get string representation of the UFile.

        Returns:
            UUri as a string.
        """
        return self.as_uri()

    def __eq__(self, other: object) -> bool:
        """Test equality to another UFile by ucfs.

        Args:
            other: Object to compare.

        Returns:
            True if both are UFiles with the same ucfs, otherwise False.
        """
            return self.ucfs == other.ucfs
        return False

    def __hash__(self) -> int:
        """Compute a hash value for the UFile based on its ucfs.

        This ensures that two UFile instances with the same ucfs will
        have the same hash value, making them behave correctly in
        hash-based collections like sets and dictionaries.

        Returns:
            An integer hash value derived from the ucfs attribute.
        """
        return hash(self.ucfs)

        """Lexical comparison by ucfs for sorting.

        Args:
            other: UFile to compare.

        Returns:
            True if this ucfs is less than other's.
        """
            return self.ucfs < other.ucfs
        return False

    @property
    def object_name(self) -> str:
        """The object name portion from the UUri.

        Returns:
            The object name.
        """
        return self.uuri.get_object_name()

    @property
    def simple_name(self) -> str:
        """Returns a simplified file name (stem, no extension).

        Returns:
            Simple name string.
        """
        object_name = self.object_name
        return object_name.split("/")[-1].rsplit(".", maxsplit=1)[0].replace(".", "-")

    @property
    def ucfs(self) -> str:
        """Unique content file string for this UFile.

        Returns:
            String in the format object_name@hash.
        """
        if self._ucfs is None:
            return f"{self.object_name}@{self.hash}"
        return self._ucfs

    def __deepcopy__(self, memo: dict) -> UFile:
        """Create a deep copy of this UFile.

        Args:
            memo: The copy memo dict.

        Returns:
            A deep copy of the UFile, with private attributes set to None.
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
    def hash(self) -> str:
        """The hash checksum for this file.

        Returns:
            The hash string using the algorithm specified in the configuration. Will be calculated if missing.
        """
        if hash_algorithm not in self.tags:
            self.tags.update(
                {
                        input_file=self.path,
                        hash_algorithm=hash_algorithm,
                    ),
                },
            )
        return self.tags[hash_algorithm]

    @property
    def uftype(self) -> str:

        Returns:
            The uftype string, or 'UNKNOWN' if not defined.
        """
        uftype = self.tags.get("uftype", None)
        if uftype is None:
        return uftype

    def download(self) -> None:
    def upload(
        self,
        overwrite: bool = True,
        verify: bool = False,
        retries: int = 3,
    ) -> None:

    @property

        Returns:
            The initialized IO instance.
        """
        if self._io is None:
            self._io = self.init_io_class()
        return self._io

    @classmethod
    def from_path_object(
        cls,
        path_object: Path,
        number_of_parents: int = 1,
        query: str | None = None,
    ) -> UFile:
        """Construct a UFile from a filesystem Path.

        Args:
            path_object: Path object for the file.
            number_of_parents: How many parent directories to include in the UUri.
            query: Optional query string for tags.

        Returns:
            A new UFile instance.
        """
        basefolder = path_object.parent.resolve()
        container_content = path_object.name
        for _ in range(number_of_parents):
            container_content = Path(basefolder.name) / container_content
            basefolder = basefolder.parent.resolve()

    def as_uri(
        self,
        scheme: str | None = None,
        netloc: str | None = None,
        path: str | None = None,
        fragment: str | None = None,
        query: str | None = None,
    ) -> str:
        """Get a string UUri representation of this file, optionally overriding UUri components.

        Args:
            scheme: Override the scheme.
            netloc: Override the network location.
            path: Override the path.
            fragment: Override the fragment (object name).
            query: Override the query string.

        Returns:
            The UUri as a string.
        """
        unparse_args = []
        if scheme is None:
            parsed_schema = self.uuri.scheme
            if parsed_schema is None:
                return self.uuri.fragment
            unparse_args.append(parsed_schema)
        else:
            unparse_args.append(scheme)
        if netloc is None:
            unparse_args.append(self.uuri.netloc)
        else:
            unparse_args.append(netloc)
        if path is None:
            unparse_args.append(self.uuri.path)
        else:
            unparse_args.append(path)
        unparse_args.append(self.uuri.params)
        if query is None:
            unparse_args.append(
                "&".join([f"{k}={v}" for k, v in sorted(self.tags.items())]),
            )
        else:
            unparse_args.append(query)
        if fragment is None:
            unparse_args.append(self.uuri.fragment)
        else:
            unparse_args.append(fragment)

        return str(urlunparse(unparse_args))

    @property
    def storage_base_uri(self) -> str:
        """The storage base UUri, omitting query and fragment.

        Returns:
            The storage base UUri as a string.
        """
        return self.as_storage_base_uri()

    def as_storage_base_uri(self) -> str:
        """Get the storage base UUri, omitting query and fragment.

        Returns:
            The storage base UUri as a string.
        """
        return f"{self.uuri.scheme}://{self.uuri.netloc}{self.uuri.path}"

        """Initialize the IO backend for this file, based on the UUri scheme.

        Returns:
            The IO class instance for this file.

        Raises:
            ImportError: If the IO backend is not installed.
        """
        scheme = self.uuri.scheme
        if scheme not in available_io_classes:
            msg = (
            )
            raise ImportError(msg)

    def get_object(self) -> Path | None:
        """Get a local object from remote storage if it exists.

        Returns:
            The path to the local object, or None if it does not exist remotely.
        """
        return self.io.get_object()

    def remote_object_exists(self) -> bool:
        """Check if the remote object exists.

        Returns:
            True if the remote object exists, False otherwise.
        """
        return self.io.remote_object_exists()

    def recalculate_hashes(self, force_local: bool = False) -> None:
        """Recalculate configured file hash for this file.

        Args:
            force_local: If True, always use the local file.
        """
        if force_local is True:
            if self.io.scratch_path.exists():
                    self.io.scratch_path,
                )
            else:
                msg = f"Cannot force calculation from local file as {self.io.scratch_path} does not exist."
                raise FileNotFoundError(msg)
        else:
                self.path,
            )

    def rebase(
        self,
        uri: str | None = None,
        upload: bool = False,
        **kwargs: P.kwargs,
    ) -> None:
        """Change this UFile's UUri and (optionally) upload it to new storage.

        Args:
            uri: New UUri string.
            upload: If True, upload the file after rebasing.
            **kwargs: Passed to upload().
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

        """Compress this UFile into a new compressed file.

        Args:
            compression_format: The format to use: 'zip', 'gz', or 'tar'.

        Returns:
            A new compressed UFile.

        Raises:
            NotImplementedError: If the format is unsupported.
        """
        if compression_format == "zip":
            suffix = ".zip"
            new_path = self.path.with_suffix(self.path.suffix + suffix)
            with ZipFile(new_path, "w", zipfile.ZIP_DEFLATED) as file:
                file.write(self.path, arcname=self.path.name)

        elif compression_format == "gz":
            suffix = ".gz"
            new_path = self.path.with_suffix(self.path.suffix + suffix)
            with self.path.open("rb") as file, gzip.open(new_path, "w") as out_file:
                out_file.writelines(file)

        elif compression_format == "tar":
            suffix = ".tar"
            new_path = self.path.with_suffix(self.path.suffix + suffix)
            with tarfile.open(new_path, mode="w:") as file:
                file.add(self.path, arcname=self.path.name)

        else:
                "Unsupported compression format. Valid options are zip, gz, and tar",
            )
            msg = "Unsupported compression format."
            raise NotImplementedError(msg)

        msg = f"Compressed UFile to {compressed_ufile.as_uri()}"
        return compressed_ufile

    def _unpack_gz(self, gz_output: str | Path, encoding: str = "utf-8") -> None:
        """Decompress a .gz file to an output file.

        Args:
            gz_output: Where to write the decompressed data.
            encoding: Encoding to use for output.
        """
        with (
            self.path.open("rb") as gz_file,
            gz_output.open("w", encoding=encoding) as out_file,
        ):
            decom_str = gzip.decompress(gz_file.read()).decode(encoding=encoding)
            out_file.write(decom_str)

    def uncompress(
        self,
        compression_format: str | None = None,
        recursive: bool = True,
        """Uncompress this UFile (auto-detecting format if needed).

        Args:
            compression_format: The format to uncompress. If None, will be auto-detected.
            recursive: If True, recursively uncompress nested archives.

        Returns:
            UFileList containing all uncompressed files.

        Raises:
            NotImplementedError: If the format is unsupported.
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
                    self.uuri.path,
                ).uncompress(temp_folder)
            case "bz2":
                temp_folder.mkdir(parents=True, exist_ok=True)
                with bz2.BZ2File(self.path) as bz_file:
                    file_names = [str(self.path.with_suffix("").name)]
                    with temp_folder / file_names[0].open("wb") as f:
                        shutil.copyfileobj(bz_file, f)
            case _:
                    "Unsupported compression format. Valid options are zip, bz2, tar, split_tar and gz",
                )
                msg = "Unsupported compression format."
                raise NotImplementedError(msg)
        return self._uncompress_recursive(
            ufl=uncompressed_ufilelist,
            recursive=recursive,
        )

    @staticmethod
    def _uncompress_recursive(
        recursive: bool = False,
        """Recursively uncompress UFileLists.

        Args:
            ufl: UFileList to uncompress.
            recursive: Whether to recursively uncompress nested archives.

        Returns:
            The uncompressed UFileList.
        """
        if recursive is True:
            for uf in ufl:
                        "Uncompressed UFile is a tar archive which will be unpacked.",
                    )
                    try:
                        ufl += uf.uncompress()
                        ufl.remove(uf)
                        Path.unlink(uf.path)
                    except (FileExistsError, IsADirectoryError, NotADirectoryError):
                            "Tarball contains folder with identical name renaming tarfile.",
                        )
                        to_be_removed = uf.path
                        ufl.remove(uf)
                        uf.rebase(
                            uri=f"#{uf.object_name}.renamed",
                            upload=True,
                        )
                        ufl += uf.uncompress(recursive=False)
                        Path.unlink(to_be_removed)
                        uf.purge_local()
        return ufl

    def create_container(self) -> None:
        """Create the remote container (e.g., bucket or folder) for this file."""
        self.io.create_container()

    def remove_remote_object(self) -> None:
        """Remove this object from remote storage."""
        self.io.remove_remote_object()

    def purge_local(self) -> None:
        """Remove the local file and its tags from the scratch disk."""
        self.purge_local_file()
        self.purge_local_tags()

    def purge_local_file(self) -> None:
        """Remove only the local file from the scratch disk."""
        with contextlib.suppress(FileNotFoundError):
            self.io.scratch_path.unlink()

    def purge_local_tags(self) -> None:
        """Remove only the cached local tags for this UFile."""
        self._tags = None

        """List all objects in the remote container.

        Returns:
            List of object names.
        """

    def identify_lineage_root_files(self, use_umeta: bool = True) -> list:
        """List root files in the lineage graph, optionally using UMeta.

        Args:
            use_umeta: If True, use UMeta interface, else reconstruct from tags.

        Returns:
            List of root object names.
        """
        if self._lineage_root_files is None:
            graph = self.create_lineage_graph(use_umeta=use_umeta)
            self._lineage_root_files = [
                node for node, in_degree in graph.in_degree() if in_degree == 0
            ]
        return self._lineage_root_files

    def create_lineage_graph(self, use_umeta: bool = True) -> nx.DiGraph:
        """Create a directed graph representing the lineage for this UFile.

        Args:
            use_umeta: Use UMeta to reconstruct lineage if True.

        Returns:
            The directed graph of UFile lineage.
        """
        if self._lineage_graph is None:
            if use_umeta is True:
                    ucfs=self.ucfs,
                    storage_base_uri=self.as_storage_base_uri(),
                )
                graph = ur.graph
            else:
                graph = nx.DiGraph()
                graph = self._walk_via_objects(
                    graph=graph,
                    ufile=self,
                )
            self._lineage_graph = graph
        return self._lineage_graph

        """Recursively walk parent relationships and build a lineage graph.

        Args:
            graph: Graph to update.
            ufile: The current UFile node.

        Returns:
            The updated graph.
        """
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
        """List the object names of direct parent files for this UFile.

        Returns:
            List of parent object names.
        """

    def simplify_name(
        self,
        source_object_names: set,
        prefix: str | None = None,
        suffix: str | None = None,
        storage_base_uri: str | None = None,
        """Rename and optionally rebase this file for user-friendly output.

        Args:
            source_object_names: Set of valid source object names to match in parents.
            prefix: Optional prefix for the new name.
            suffix: Optional suffix for the new name.
            storage_base_uri: If given, rebase the output file here.

        Returns:
            The renamed UFile, or None if no matching parent found.
        """
        matching_source = source_object_names.intersection(self.parents)
        if len(matching_source) != 1:
            msg = f"Could not find matching source file in parents for {self}"
            return None
        simple_name = ""
        if prefix is not None:
            simple_name += prefix
        simple_name += str(Path(next(iter(matching_source))).name.split(".")[0])
        if suffix is not None:
            simple_name += suffix
        if storage_base_uri is None:
            self.rebase(uri=f"#{simple_name}", upload=True, overwrite=False)
        else:
            self.rebase(
                uri=f"{storage_base_uri}#{simple_name}",
                upload=True,
                overwrite=False,
            )
        return self