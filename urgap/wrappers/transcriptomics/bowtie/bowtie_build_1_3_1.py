"""Urgap bowtie_build_1_3_1 wrapper."""

import json
import os

import urgap


class bowtie_build_1_3_1(urgap.unode.UNodeBase):
    """Urgap wrapper for the bowtie 1.3.1 short read aligner."""

    META_INFO = {
        "name": "bowtie_build_1_3_1",
        "version": "1.3.1",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "13.09.2021",
        "api_port": 42902,
        "engine_type": ("aligner", "ngs"),
        "platform_independent": False,
        "utranslation_style": "bowtie_build_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "bowtie-build",
                    "uri": None,
                    "urn": "darwin/arm64/bowtie_build_1_3_1.zip",
                    "urn_md5": "75ac9a08dfa7647db5734e2f1674c5bd",
                    "external_md5": "07dd98341f3644a5b30a8614ed8e2f82",
                    "external_url": "https://github.com/BenLangmead/bowtie/releases/download/v1.3.1/bowtie-1.3.1-macos-x86_64.zip",
                    "additional_exe": {
                        "bowtie-build-s": "bowtie-build-s",
                        "bowtie-build-l": "bowtie-build-l",
                    },
                },
                "x86_64": {
                    "exe": "bowtie-build",
                    "uri": None,
                    "urn": "darwin/x86_64/bowtie_build_1_3_1.zip",
                    "urn_md5": "75ac9a08dfa7647db5734e2f1674c5bd",
                    "external_md5": "07dd98341f3644a5b30a8614ed8e2f82",
                    "external_url": "https://github.com/BenLangmead/bowtie/releases/download/v1.3.1/bowtie-1.3.1-macos-x86_64.zip",
                    "additional_exe": {
                        "bowtie-build-s": "bowtie-build-s",
                        "bowtie-build-l": "bowtie-build-l",
                    },
                },
            },
            "linux": {
                "arm64": {
                    "exe": "bowtie-build",
                    "uri": None,
                    "urn": "linux/arm64/bowtie_build_1_3_1.zip",
                    "urn_md5": "75ac9a08dfa7647db5734e2f1674c5bd",
                    "external_md5": "823bbb508e35b104dcf8efba7263732f",
                    "external_url": "https://github.com/BenLangmead/bowtie/releases/download/v1.3.1/bowtie-1.3.1-linux-x86_64.zip",
                    "additional_exe": {
                        "bowtie-build-s": "bowtie-build-s",
                        "bowtie-build-l": "bowtie-build-l",
                    },
                },
                "x86_64": {
                    "exe": "bowtie-build",
                    "uri": None,
                    "urn": "linux/x86_64/bowtie_build_1_3_1.zip",
                    "urn_md5": "75ac9a08dfa7647db5734e2f1674c5bd",
                    "external_md5": "823bbb508e35b104dcf8efba7263732f",
                    "external_url": "https://github.com/BenLangmead/bowtie/releases/download/v1.3.1/bowtie-1.3.1-linux-x86_64.zip",
                    "additional_exe": {
                        "bowtie-build-s": "bowtie-build-s",
                        "bowtie-build-l": "bowtie-build-l",
                    },
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.transcriptomics.FASTA: {"min": 1, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.BOWTIE_1_INDEX: {"min": 1, "max": -1},
            urgap.uftypes.transcriptomics.BOWTIE_1_INDEX_MAPPING: {"min": 1, "max": 1},
        },
        "citation": """
        Langmead, B., Trapnell, C., Pop, M. et al. Ultrafast and memory-efficient alignment of short DNA sequences to the human genome.
        Genome Biol 10, R25 (2009). https://doi.org/10.1186/gb-2009-10-3-r25
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize bowtie_build_1_3_1 class."""
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
        base_output_path = utrace.output_files[0].path.parent
        fasta_files = ""
        for file in utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.FASTA,
        ):
            fasta_files += str(file) + ","
        fasta_files = fasta_files.rstrip(",")
        utrace.urun_dict.command_list = [
            str(self.exe_path),
            fasta_files,
            str(base_output_path / "new_idx"),
        ]

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for bowtie_build_1_3_1 wrapper.

        During preflight,
            - parameters are formatted
            - index files are generated using bowtie-build
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        return self.create_command_list(utrace=utrace)

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for bowtie_build_1_3_1 wrapper.

            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        output_index_files = list(utrace.output_files[0].path.parent.glob("*.ebwt"))

        for _ in range(len(output_index_files) - 1):
            utrace.extend_output_files_by_uftype(
                urgap.uftypes.transcriptomics.BOWTIE_1_INDEX,
            )
        utrace.output_files.complete_file_counts()

        index_mapping = {}
        for old_file, target_file in zip(
            output_index_files,
            utrace.output_files.get_path_objects_by_uftype(
                urgap.uftypes.transcriptomics.BOWTIE_1_INDEX,
            ),
            strict=False,
        ):
            index_mapping[target_file.name] = old_file.name
            os.rename(old_file, target_file)

        with open(
            utrace.output_files.get_path_objects_by_uftype(
                urgap.uftypes.transcriptomics.BOWTIE_1_INDEX_MAPPING,
            )[0],
            "w",
        ) as mapping_json:
            json.dump(index_mapping, mapping_json, indent=4)
        return utrace
