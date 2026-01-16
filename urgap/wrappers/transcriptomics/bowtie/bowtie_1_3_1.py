"""Urgap bowtie_1_3_1 wrapper."""

import json
import logging
import multiprocessing as mp
import os

import urgap


class bowtie_1_3_1(urgap.unode.UNodeBase):
    """Urgap wrapper for the bowtie 1.3.1 short read aligner."""

    META_INFO = {
        "name": "bowtie_1_3_1",
        "version": "1.3.1",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "13.09.2021",
        "api_port": 42901,
        "engine_type": ("aligner", "ngs"),
        "platform_independent": False,
        "utranslation_style": "bowtie_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "bowtie",
                    "uri": None,
                    "urn": "darwin/arm64/bowtie_1_3_1.zip",
                    "urn_md5": "2ed2331434145ad44ee01231041b3ea3",
                    "external_md5": "07dd98341f3644a5b30a8614ed8e2f82",
                    "external_url": "https://github.com/BenLangmead/bowtie/releases/download/v1.3.1/bowtie-1.3.1-macos-x86_64.zip",
                    "additional_exe": {
                        "bowtie-align-s": "bowtie-align-s",
                        "bowtie-align-l": "bowtie-align-l",
                    },
                },
                "x86_64": {
                    "exe": "bowtie",
                    "uri": None,
                    "urn": "darwin/x86_64/bowtie_1_3_1.zip",
                    "urn_md5": "2ed2331434145ad44ee01231041b3ea3",
                    "external_md5": "07dd98341f3644a5b30a8614ed8e2f82",
                    "external_url": "https://github.com/BenLangmead/bowtie/releases/download/v1.3.1/bowtie-1.3.1-macos-x86_64.zip",
                    "additional_exe": {
                        "bowtie-align-s": "bowtie-align-s",
                        "bowtie-align-l": "bowtie-align-l",
                    },
                },
            },
            "linux": {
                "arm64": {
                    "exe": "bowtie",
                    "uri": None,
                    "urn": "linux/arm64/bowtie_1_3_1.zip",
                    "urn_md5": "62c8c51e6eda0d0e4244bf44dd8d001f",
                    "external_md5": "823bbb508e35b104dcf8efba7263732f",
                    "external_url": "https://github.com/BenLangmead/bowtie/releases/download/v1.3.1/bowtie-1.3.1-linux-x86_64.zip",
                    "additional_exe": {
                        "bowtie-align-s": "bowtie-align-s",
                        "bowtie-align-l": "bowtie-align-l",
                    },
                },
                "x86_64": {
                    "exe": "bowtie",
                    "uri": None,
                    "urn": "linux/x86_64/bowtie_1_3_1.zip",
                    "urn_md5": "62c8c51e6eda0d0e4244bf44dd8d001f",
                    "external_md5": "823bbb508e35b104dcf8efba7263732f",
                    "external_url": "https://github.com/BenLangmead/bowtie/releases/download/v1.3.1/bowtie-1.3.1-linux-x86_64.zip",
                    "additional_exe": {
                        "bowtie-align-s": "bowtie-align-s",
                        "bowtie-align-l": "bowtie-align-l",
                    },
                },
            },
        },
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
        """Initialize bowtie_1_3_1 class."""
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
        for value in utrace.urun_dict.translations["all_params"].values():
            translated_value = value["translated_value"]
            if value["translated_key"] is not None:
                utrace.urun_dict.command_list.append(value["translated_key"])
                if (value["original_key"] == "cpus") and (translated_value == -1):
                    translated_value = mp.cpu_count() - 1
            if len(str(translated_value)) != 0:
                utrace.urun_dict.command_list.append(str(translated_value))
                if translated_value == "--un":
                    utrace.extend_output_files_by_uftype(
                        urgap.uftypes.transcriptomics.reads.FASTQ_GZ,
                    )
                    utrace.urun_dict.command_list.append(
                        str(utrace.output_files[-1].path),
                    )
        utrace.urun_dict.command_list.append("-x")
        utrace.urun_dict.command_list.append("new_idx")
        utrace.urun_dict.command_list.append(fastq_files)
        utrace.urun_dict.command_list.append(str(utrace.output_files[0].path))

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for bowtie_1_3_1 wrapper.

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
        with open(index_file) as mapping_file:
            index_mapping = json.load(mapping_file)

        # Unlink existing index files (for sanity)
        for old_link in index_file.parent.glob("*.ebwt"):
            old_link.unlink()

        for index_file in utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.BOWTIE_1_INDEX,
        ):
            os.symlink(index_file, index_file.parent / index_mapping[index_file.name])
        os.environ["BOWTIE_INDEXES"] = str(index_file.parent)
        return self.create_command_list(utrace=utrace)

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for bowtie_1_3_1 wrapper.

            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        if (
            utrace.urun_dict.translations["all_params"]["aligner_write_no_align"][
                "original_value"
            ]
            is True
        ):
            if utrace.output_files[-1].path.exists() is False:
                logging.warning(
                    "Fastq with unaligned reads not created by bowtie. Creating empty file.",
                )
                with open(utrace.output_files[-1].path, "w"):
                    pass
            fastq_gz = utrace.output_files[-1].compress(compression_format="gz").path
            os.replace(fastq_gz, utrace.output_files[-1].path)
        return utrace
