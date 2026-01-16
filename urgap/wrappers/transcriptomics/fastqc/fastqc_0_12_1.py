"""Urgap fastqc_0_12_1 wrapper."""

import multiprocessing as mp
import os

import urgap


class fastqc_0_12_1(urgap.unode.UNodeBase):
    """Urgap wrapper for FastQC 0.12.1."""

    META_INFO = {
        "name": "fastqc_0_12_1",
        "version": "1.3.1",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "13.09.2021",
        "api_port": 42907,
        "engine_type": ("ngs",),
        "platform_independent": True,
        "requires": {
            "other_uftypes": {
                "other_dependencies": ("java",),
                "python_packages": [
                    "unimod_mapper",
                ],
            },
        },
        "utranslation_style": "fastqc_style_1",
        "engine": {
            "platform_independent": {
                "arc_independent": {
                    "exe": "fastqc",
                    "uri": None,
                    "urn": "platform_independent/arc_independent/fastqc_0_12_1.zip",
                    "urn_md5": "233b8b3d25c45e63d234eeb79c9b0ec9",
                    "external_md5": "a628c84cf19235d47fd979d4bb786a60",
                    "external_url": "https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.12.1.zip",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.transcriptomics.reads.ANY: {"min": 1, "max": 1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.FASTQC_HTML: {"min": 1, "max": 1},
            urgap.uftypes.transcriptomics.FASTQC_ZIP: {"min": 1, "max": 1},
        },
        "citation": """
        Babraham Bioinformatics group.
        https://www.bioinformatics.babraham.ac.uk/publications.html
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize fastqc_0_12_1 class."""
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
            new_uri = f"{ufile.as_storage_base_uri()}/{top_level_folder_name}#{ufile.object_name.replace(top_level_folder_name + '/', '', 1)}"
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
        utrace.urun_dict.command_list = [
            str(self.exe_path),
        ]
        for value in utrace.urun_dict.translations["all_params"].values():
            if value["translated_value"] is None:
                continue
            if value["translated_key"] is not None:
                utrace.urun_dict.command_list.append(value["translated_key"])
                if (value["original_key"] == "cpus") and (
                    value["translated_value"] == -1
                ):
                    value["translated_value"] = mp.cpu_count() - 1
            utrace.urun_dict.command_list.append(str(value["translated_value"]))
        utrace.urun_dict.command_list.append("-o")
        utrace.urun_dict.command_list.append(str(utrace.output_files[0].path.parent))
        utrace.urun_dict.command_list.append(str(utrace.input_files[0].path))

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for fastqc_0_12_1 wrapper.

        During preflight,
            - parameters are formatted
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
        """Postflight routine for fastqc_0_12_1 wrapper.

        FastQC removes the last suffix of the input file name and adds _fastqc + suffix.
        These files are renamed to conform to the urgap output files.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        # Only some suffixes are removed by FastQC
        input_file_name = utrace.input_files[0].object_name.split("/")[-1]
        for suffix in (".gz", ".fastq", ".sam", ".bam"):
            input_file_name = input_file_name.removesuffix(suffix)
        output_file_base_name = ".".join(input_file_name.split(".")) + "_fastqc"
        for opath in utrace.output_files.get_path_object_groups_by_uftypes().values():
            os.rename(
                utrace.output_files[0].path.parent
                / f"{output_file_base_name}{opath[0].suffix}",
                opath[0],
            )
        return utrace
