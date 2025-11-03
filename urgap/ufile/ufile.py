"""UFile module of urgap2."""

from __future__ import annotations

import bz2
import contextlib
import copy
import gzip
import hashlib
import json
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

import urgap

P = ParamSpec("P")

logger = logging.getLogger(__name__)


class UFile:
    """Urgap pipeline file interface."""

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

        self.uuri = urgap.UUri(
            uri=self.uri,
        )
        self._io = None
        self._ucfs = None

    def format_uri(self) -> None:
        """Format the URI if storage_base_uri and ucfs combination was used to construct uri."""
        if "@" in self.uri:
            hash_algorithm = urgap.config["hash_algorithm"]
            uri, ucfs_hash = self.uri.split("@")
            self.uri = urgap.ucore.append_query_to_uri(
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
                    logger.debug(
                        "Remote has no tags, thus the file is not downloaded again."
                        " Delete local explicitly UFile.purge_local_files() if needed.",
                    )
                download_file = False
            elif remote_tags.get(urgap.config["hash_algorithm"], None) is None:
                logger.debug(
                    "Remote has tag capability but hash was not set."
                    " Will not download file anymore."
                    " Delete local explicitly UFile.purge_local_files() if needed.",
                )
                download_file = False
            else:
                if urgap.config["hash_algorithm"] not in self.tags:
                    self.tags.update(
                        {
                            urgap.config[
                                "hash_algorithm"
                            ]: urgap.ucore.calculate_file_hash(
                                self.io.scratch_path,
                                hash_algorithm=urgap.config["hash_algorithm"],
                            ),
                        },
                    )
                if self.tags.get(
                    urgap.config["hash_algorithm"],
                    None,
                ) != remote_tags.get(urgap.config["hash_algorithm"], None):
                    logger.debug(
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
        if isinstance(other, urgap.UFile) is True:
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

    def __lt__(self, other: urgap.UFile) -> bool:
        """Lexical comparison by ucfs for sorting.

        Args:
            other: UFile to compare.

        Returns:
            True if this ucfs is less than other's.
        """
        if isinstance(other, urgap.UFile) is True:
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
        hash_algorithm = urgap.config["hash_algorithm"]
        if hash_algorithm not in self.tags:
            self.tags.update(
                {
                    hash_algorithm: urgap.ucore.calculate_file_hash(
                        input_file=self.path,
                        hash_algorithm=hash_algorithm,
                    ),
                },
            )
        return self.tags[hash_algorithm]

    @property
    def uftype(self) -> str:
        """The Urgap file type for this file.

        Returns:
            The uftype string, or 'UNKNOWN' if not defined.
        """
        uftype = self.tags.get("uftype", None)
        if uftype is None:
            uftype = urgap.uftypes.unknown.UNKNOWN
        return uftype

    def download(self) -> None:
        """Download this file from remote storage to local scratch."""
        if urgap.utl.tracing_enabled is True:
            span_context = [
                "ufile-download",
                self.object_name,
            ]
            urgap.utl.init_span(span_context, attributes={"id": "ufile-download"})
            self.io.download()
            urgap.utl.increase_counter("ufiles-downloaded")
            file_size_mbytes = Path(self.io.scratch_path).stat().st_size / (1024 * 1024)
            urgap.utl.set_span_attributes(
                span_context,
                {
                    "size in MB": file_size_mbytes,
                    "ufiles-size-transfered-in-MB": file_size_mbytes,
                },
            )
            urgap.utl.close_span(span_context)
        else:
            self.io.download()

    def upload(
        self,
        overwrite: bool = True,
        verify: bool = False,
        purge: bool = True,
        retries: int = 3,
    ) -> None:
        """Upload this file to remote storage.

        Args:
            overwrite: If True, always upload, overwriting existing remote files.
            verify: If True, check that the remote hash matches local; re-upload if needed.
            purge: If True, remove the local copy of the file after a successful upload.
            retries: Number of times to retry verification on failure.
        """
        if urgap.utl.tracing_enabled is True:
            span_context = [
                "ufile-upload",
                self.object_name,
            ]
            urgap.utl.init_span(span_context, attributes={"id": "ufile-upload"})
        self.recalculate_hashes(force_local=overwrite)
        if overwrite is True:
            self.io.upload(tags=self.tags)
        else:
            remote_tags = self.io.get_remote_tags()
            if remote_tags is None:
                logger.info("No remote tags found. Uploading missing file.")
                self.io.upload()
            elif self.hash == remote_tags.get(urgap.config["hash_algorithm"]):
                logger.info("Remote hash matches local one. Not uploading again.")
            else:
                logger.info("Remote hash differs from local one. Uploading again.")
                self.io.upload()
        if verify is True:
            for attempt in range(retries + 1):
                uf = urgap.UFile(uri=self.as_uri(query=""))
                remote_hash = urgap.ucore.calculate_file_hash(
                    uf.path,
                    urgap.config["hash_algorithm"],
                )
                if remote_hash == self.hash:
                    logger.debug("Upload verified successfully.")
                    break
                msg = f"Verification failed (attempt #{attempt + 1}). Re-trying."
                logger.warning(msg)
                self.recalculate_hashes()
                self.io.upload(tags=self.tags)
            else:
                msg = "Could not upload file - hash mismatch after retries."
                logger.error(msg)
                raise OSError(msg)
        if urgap.utl.tracing_enabled is True:
            file_size_mbytes = Path(self.io.scratch_path).stat().st_size / (1024 * 1024)
            urgap.utl.set_span_attributes(
                span_context,
                {
                    "size in MB": file_size_mbytes,
                    "uftype": self.tags.get("uftype", None),
                    "scheme": self.io.uuri.scheme,
                    "path": self.io.uuri.path,
                },
            )
            urgap.utl.increase_counter("ufiles-uploaded")
            urgap.utl.increase_counter(
                "ufiles-size-transfered-in-MB",
                file_size_mbytes,
            )
            urgap.utl.close_span(span_context)
        if purge:
            self.purge_local_file()

    @property
    def io(self) -> urgap.io:
        """IO property to access the Urgap IO backend for this file.

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
        uri = f"file://{basefolder}?{query}#{container_content}"
        return UFile(uri=uri)

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

    def init_io_class(self) -> urgap.UFile.io:
        """Initialize the IO backend for this file, based on the UUri scheme.

        Returns:
            The IO class instance for this file.

        Raises:
            ImportError: If the IO backend is not installed.
        """
        scheme = self.uuri.scheme
        available_io_classes = urgap.instances.ufile_io_manager.available_io_classes
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
                hash_value = urgap.ucore.calculate_file_hash(
                    self.io.scratch_path,
                    hash_algorithm=urgap.config["hash_algorithm"],
                )
            else:
                msg = f"Cannot force calculation from local file as {self.io.scratch_path} does not exist."
                raise FileNotFoundError(msg)
        else:
            hash_value = urgap.ucore.calculate_file_hash(
                self.path,
                hash_algorithm=urgap.config["hash_algorithm"],
            )
        self.tags.update({urgap.config["hash_algorithm"]: hash_value})

    def rebase(
        self,
        uri: str | None = None,
        upload: bool = False,
        **kwargs: P.kwargs,
    ) -> None:
        """Change this UFile's UUri and (optionally) upload it to new storage.

        If the provided URI has no query string, clear dynamic tags (e.g. ``md5``,
        ``parent_*``) but **preserve structural tags** like ``uftype`` so downstream
        logic (e.g. rerun/skip) keeps working.

        Args:
            uri: New UUri string.
            upload: If True, upload the file after rebasing.
            **kwargs: Passed to upload().
        """
        _ = self.path  # call path property to ensure download of file before rebasing
        old_scratch = self.io.scratch_path

        parsed_uri = urlparse(uri)

        preserve_keys = {"uftype"}
        preserved: dict[str, object] = {}
        if parsed_uri.query == "":
            try:
                preserved = {
                    k: v for k, v in (self.tags or {}).items() if k in preserve_keys
                }
            except AttributeError:
                preserved = {}

        new_uri = self.as_uri(
            scheme=None if parsed_uri.scheme == "" else parsed_uri.scheme,
            netloc=None if parsed_uri.netloc == "" else parsed_uri.netloc,
            path=None if parsed_uri.path == "" else parsed_uri.path,
            fragment=None if parsed_uri.fragment == "" else parsed_uri.fragment,
            query="" if parsed_uri.query == "" else parsed_uri.query,
        )

        self._io = None
        self.uuri = urgap.UUri(uri=new_uri)

        if parsed_uri.query == "" and preserved:
            keep_query = "&".join(f"{k}={v}" for k, v in preserved.items())
            self.uuri = urgap.UUri(
                uri=urgap.ucore.append_query_to_uri(
                    uri=self.as_uri(),
                    query=keep_query,
                ),
            )
        self._tags = None

        try:
            shutil.copyfile(old_scratch, self.io.scratch_path)
        except (shutil.SameFileError, FileNotFoundError):
            logger.debug("Could not move file for %s", new_uri)

        if upload:
            self.upload(**kwargs)

    def compress(self, compression_format: str) -> urgap.UFile:
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
            logger.error(
                "Unsupported compression format. Valid options are zip, gz, and tar",
            )
            msg = "Unsupported compression format."
            raise NotImplementedError(msg)

        compressed_ufile = urgap.UFile(uri=self.as_uri() + suffix)
        msg = f"Compressed UFile to {compressed_ufile.as_uri()}"
        logger.info(msg)
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
    ) -> urgap.UFileList:
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
            compression_format = urgap.util.sense_compression_format(self.path)
        wid = urgap.uwid_obj.generate_wid()
        temp_folder = urgap.scratch_disk_base / wid / "uncompress"
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
                urgap.UFileList.from_folder(
                    self.uuri.path,
                    download=True,
                ).uncompress(temp_folder)
            case "bz2":
                temp_folder.mkdir(parents=True, exist_ok=True)
                with bz2.BZ2File(self.path) as bz_file:
                    file_names = [str(self.path.with_suffix("").name)]
                    with temp_folder / file_names[0].open("wb") as f:
                        shutil.copyfileobj(bz_file, f)
            case _:
                logger.error(
                    "Unsupported compression format. Valid options are zip, bz2, tar, split_tar and gz",
                )
                msg = "Unsupported compression format."
                raise NotImplementedError(msg)
        uncompressed_ufilelist = urgap.UFileList.from_folder(temp_folder)
        return self._uncompress_recursive(
            ufl=uncompressed_ufilelist,
            recursive=recursive,
        )

    @staticmethod
    def _uncompress_recursive(
        ufl: urgap.UFileList,
        recursive: bool = False,
    ) -> urgap.UFileList:
        """Recursively uncompress UFileLists.

        Args:
            ufl: UFileList to uncompress.
            recursive: Whether to recursively uncompress nested archives.

        Returns:
            The uncompressed UFileList.
        """
        if recursive is True:
            for uf in ufl:
                if urgap.util.sense_compression_format(uf.path) == "tar":
                    logger.info(
                        "Uncompressed UFile is a tar archive which will be unpacked.",
                    )
                    try:
                        ufl += uf.uncompress()
                        ufl.remove(uf)
                        Path.unlink(uf.path)
                    except (FileExistsError, IsADirectoryError, NotADirectoryError):
                        logger.warning(
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

    def list_container_items(
        self,
        pattern: str | None = None,
        limit: int = 1000,
        full_string: bool = False,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list:
        """List all objects in the remote container.

        Args:
            pattern: Regex pattern for filtering object names.
            limit: Maximum number of files to request in one query.
            full_string: Whether to return the list with full strings or just fragments.

        Returns:
            List of object names.
        """
        return self.io.list_container_items(
            pattern=pattern,
            limit=limit,
            full_string=full_string,
            start_date=start_date,
            end_date=end_date,
        )

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
                ur = urgap.UReport(
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

    def _walk_via_objects(self, graph: nx.DiGraph, ufile: urgap.UFile) -> nx.DiGraph:
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
            parent_ufile = urgap.UFile(uri=parent_uri)
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
        parents_str = self._get_multi_part_tag(tag_name="parent")
        if parents_str is None:
            return []
        return parents_str.split(",")

    @property
    def provenance(
        self,
    ) -> None | nx.DiGraph:
        """Provenance of UFile as a directed graph.

        Returns:
            None or provenance representation as NX DiGraph.
        """
        dot_str = self._get_multi_part_tag(tag_name="dot_str")
        if dot_str is None:
            return None

    def _get_multi_part_tag(self, tag_name: str) -> str | None:
        """Decompress and decode a potentially multi-part tag."""
        tag = ""
        i = 0
        while self.tags.get(f"{tag_name}_{i}", None) is not None:
            tag += self.tags[f"{tag_name}_{i}"]
            i += 1
        if i > 0:
            return zlib.decompress(b64decode(tag)).decode()
        return None

    def simplify_name(
        self,
        source_object_names: set,
        prefix: str | None = None,
        suffix: str | None = None,
        storage_base_uri: str | None = None,
    ) -> urgap.UFile | None:
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
            logger.error(msg)
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