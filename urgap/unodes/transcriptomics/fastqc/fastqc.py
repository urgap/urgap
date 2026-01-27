"""Urgap FastQC wrapper."""

import multiprocessing as mp

import urgap


class FastQC(urgap.unode.UNodeBase):
    """Urgap wrapper for FastQC.

    https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.12.1.zip

    Note:
        Requires python package 'unimod_mapper' and 'java' installed in the environment.
    """

    META_INFO = {
        "name": "FastQC",
        "versions": [
            {
                "version": "0.12.1",
                "exe_path": "$fastqc",
            },
        ],
        "parameters_not_triggering_rerun": ["-t"],
        "engine": None,
        "engine_type": ("ngs",),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
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
        """Initialize FastQC class."""
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
        if "-t" not in utrace.urun_dict:
            utrace.urun_dict.command_list.extend(["-t", str(mp.cpu_count() - 1)])
        for k, v in utrace.urun_dict.items():
            utrace.urun_dict.command_list.extend([k, v])
        utrace.urun_dict.command_list.append("-o")
        utrace.urun_dict.command_list.append(str(utrace.output_files[0].path.parent))
        utrace.urun_dict.command_list.append(str(utrace.input_files[0].path))

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for FastQC wrapper.

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
        """Postflight routine for FastQC wrapper.

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
        for (
            opath,
        ) in utrace.output_files.get_path_object_groups_by_uftypes().values():
            (
                utrace.output_files[0].path.parent
                / f"{output_file_base_name}{opath[0].suffix}"
            ).rename(opath[0])
        return utrace
