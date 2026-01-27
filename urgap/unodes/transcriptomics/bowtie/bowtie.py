"""Urgap Bowtie wrapper."""

import json
import logging
import multiprocessing as mp
import os

from pathlib import Path

import urgap


class Bowtie(urgap.unode.UNodeBase):
    """Urgap wrapper for the bowtie short read aligner.

    https://github.com/BenLangmead/bowtie/releases
    """

    META_INFO = {
        "name": "Bowtie",
        "versions": [
            {
                "version": "1.3.1",
                "exe_path": "$bowtie",
            },
        ],
        "parameters_not_triggering_rerun": ["--threads"],
        "engine": None,
        "engine_type": ("aligner", "ngs"),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "input_uftypes": {
            urgap.uftypes.transcriptomics.BOWTIE_1_INDEX_MAPPING: {"min": 1, "max": 1},
            urgap.uftypes.transcriptomics.BOWTIE_1_INDEX: {"min": 1, "max": -1},
            urgap.uftypes.transcriptomics.reads.FASTQ_GZ: {"min": 1, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.BOWTIE_1_ALIGNMENT: {"min": 1, "max": 1},
            urgap.uftypes.transcriptomics.reads.FASTQ_GZ: {"min": 0, "max": 1},
        },
        "citation": """
        Langmead, B., Trapnell, C., Pop, M. et al. Ultrafast and memory-efficient alignment of short DNA sequences to the human genome.
        Genome Biol 10, R25 (2009). https://doi.org/10.1186/gb-2009-10-3-r25
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize Bowtie class."""
        super().__init__(*args, **kwargs)

    def prep_urgap_package_structure(
        self,
        external_ufile_list: urgap.UFileList,
    ) -> urgap.UFileList:
        """Prepare resource specific package structure.

        The wrapper can define a process which transforms the content
        of the external resource to the urgap resource format.

        This function is called from unode._prepare_urgap_packages, if
        available.

        Args:
            external_ufile_list: Unpacked external resource as ufiles.

        Returns:
            Processed UFileList.
        """
        new_ufile_list = urgap.UFileList()
        top_level_folder_name = external_ufile_list[0].uuri.fragment.split("/")[0]
        for ufile in external_ufile_list:
            new_uri = f"{ufile.as_storage_base_uri()}/{top_level_folder_name}#{ufile.object_name.replace(top_level_folder_name + '/', '')}"
            new_ufile_list.append(urgap.UFile(uri=new_uri))

        return new_ufile_list

    def create_command_list(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Create the command list from input parameters.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        fastq_files = ""
        for file in utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.reads.FASTQ_GZ,
        ):
            fastq_files += str(file) + ","
        fastq_files = fastq_files.rstrip(",")
        utrace.urun_dict.command_list.append(str(self.exe_path))
        if "--threads" not in utrace.urun_dict:
            utrace.urun_dict.command_list.extend(["--threads", str(mp.cpu_count() - 1)])
        for k, v in utrace.urun_dict.items():
            if k == "--un":
                utrace.extend_output_files_by_uftype(
                    urgap.uftypes.transcriptomics.reads.FASTQ_GZ,
                )
                utrace.urun_dict.command_list.extend(
                    [k, str(utrace.output_files[-1].path)],
                )
                continue
            utrace.urun_dict.command_list.extend([k, v])
            utrace.urun_dict.command_list.append(fastq_files)
        utrace.urun_dict.command_list.append(str(utrace.output_files[0].path))

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for Bowtie wrapper.

        During preflight,
            - parameters are formatted
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        index_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.BOWTIE_1_INDEX_MAPPING,
        )[0]
        # Create the symlinks since file names have to be static
        with index_file.open() as mapping_file:
            index_mapping = json.load(mapping_file)

        # Unlink existing index files (for sanity)
        for old_link in index_file.parent.glob("*.ebwt"):
            old_link.unlink()

        for index_file in utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.BOWTIE_1_INDEX,
        ):
            (index_file.parent / index_mapping[index_file.name]).symlink_to(index_file)
        os.environ["BOWTIE_INDEXES"] = str(index_file.parent)
        utrace = self.create_command_list(utrace=utrace)
        return utrace  # noqa: RET504

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for Bowtie wrapper.

            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        if utrace.output_files[-1].path.exists() is False:
            logging.warning(
                "Fastq with unaligned reads not created by bowtie. Creating empty file.",
            )
            with utrace.output_files[-1].path.open("w"):
                pass
            fastq_gz = utrace.output_files[-1].compress(compression_format="gz").path
            Path(fastq_gz).replace(utrace.output_files[-1].path)
        return utrace