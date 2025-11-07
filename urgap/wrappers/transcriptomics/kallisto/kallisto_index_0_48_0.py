"""Urgap kallisto_0_48_0 wrapper."""

import os

import urgap


class kallisto_index_0_48_0(urgap.unode.UNodeBase):
    """Urgap wrapper for the kallisto index builder 0.48.0."""

    META_INFO = {
        "name": "kallisto_index_0_48_0",
        "version": "1.3.1",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "13.09.2021",
        "api_port": 42908,
        "engine_type": ("aligner", "ngs"),
        "platform_independent": False,
        "utranslation_style": "kallisto_index_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "kallisto",
                    "uri": None,
                    "urn": "darwin/arm64/kallisto_index_0_48_0.zip",
                    "external_md5": "d4f77c03d3e20d3f70b2e4a17a742232",
                    "external_url": "https://github.com/pachterlab/kallisto/releases/download/v0.48.0/kallisto_mac-v0.48.0.tar.gz",
                },
                "x86_64": {
                    "exe": "kallisto",
                    "uri": None,
                    "urn": "darwin/x86_64/kallisto_index_0_48_0.zip",
                    "external_md5": "d4f77c03d3e20d3f70b2e4a17a742232",
                    "external_url": "https://github.com/pachterlab/kallisto/releases/download/v0.48.0/kallisto_mac-v0.48.0.tar.gz",
                },
            },
            "linux": {
                "arm64": {
                    "exe": "kallisto",
                    "uri": None,
                    "urn": "linux/arm64/kallisto_index_0_48_0.zip",
                    "urn_md5": "d76f7a72e25249fe620af6cac8b9a9bc",
                    "external_md5": "3163f6182960fdf7c7c008200b2723a0",
                    "external_url": "https://github.com/pachterlab/kallisto/releases/download/v0.48.0/kallisto_linux-v0.48.0.tar.gz",
                },
                "x86_64": {
                    "exe": "kallisto",
                    "uri": None,
                    "urn": "linux/x86_64/kallisto_index_0_48_0.zip",
                    "urn_md5": "d76f7a72e25249fe620af6cac8b9a9bc",
                    "external_md5": "3163f6182960fdf7c7c008200b2723a0",
                    "external_url": "https://github.com/pachterlab/kallisto/releases/download/v0.48.0/kallisto_linux-v0.48.0.tar.gz",
                },
            },
            "win32": {
                "x86_64": {
                    "exe": "kallisto",
                    "uri": None,
                    "urn": "win32/x86_64/kallisto_index_0_48_0.zip",
                    "external_md5": "4d2fb284cd3fa4b9c6536324f490578c",
                    "external_url": "https://github.com/pachterlab/kallisto/releases/download/v0.48.0/kallisto_windows-v0.48.0.zip",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.transcriptomics.FASTA: {"min": 1, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.KALLISTO_INDEX: {"min": 1, "max": 1},
        },
        "citation": """
        NL Bray, H Pimentel, P Melsted and L Pachter, Near optimal probabilistic RNA-seq quantification.
        Nature Biotechnology 34, p 525--527 (2016).
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize kallisto_index_0_48_0 class."""
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
        fasta_files = ""
        for file in utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.FASTA,
        ):
            fasta_files += str(file) + ","
        fasta_files = fasta_files.rstrip(",")

        utrace.urun_dict.command_list.append(str(self.exe_path))
        utrace.urun_dict.command_list.append("index")
        utrace.urun_dict.command_list.append("-i")

        utrace.urun_dict.command_list.append(
            utrace.output_files[0].object_name.split("/")[-1],
        )

        for value in utrace.urun_dict.translations["all_params"].values():
            option = value["translated_key"] + " " + value["translated_value"]
            utrace.urun_dict.command_list.append(option)

        utrace.urun_dict.command_list.append(fasta_files)

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for kallisto_index_0_48_0 wrapper.

        During preflight,
            - parameters are formatted
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace = self.create_command_list(utrace=utrace)
        self._old_wd = os.getcwd()
        os.chdir(utrace.output_files[0].path.parent)
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for kallisto_index_0_48_0 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        os.chdir(self._old_wd)
        return utrace
