"""Urgap KallistoQuant wrapper."""

import urgap


class KallistoQuant(urgap.unode.UNodeBase):
    """Urgap wrapper for the kallisto quant builder.

    https://github.com/pachterlab/kallisto/releases
    """

    META_INFO = {
        "name": "KallistoQuant",
        "versions": [
            {
                "version": "0.51.1",
                "exe_path": "$kallisto",
            },
        ],
        "parameters_not_triggering_rerun": [],
        "engine": None,
        "engine_type": ("aligner", "quantification", "ngs"),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "input_uftypes": {
            urgap.uftypes.transcriptomics.KALLISTO_INDEX: {"min": 1, "max": 1},
            urgap.uftypes.transcriptomics.reads.FASTQ_GZ: {"min": 1, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.KALLISTO_QUANT_TSV: {"min": 1, "max": 1},
        },
        "citation": """
        NL Bray, H Pimentel, P Melsted and L Pachter, Near optimal probabilistic RNA-seq quantification.
        Nature Biotechnology 34, p 525--527 (2016).
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize KallistoQuant class."""
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
        fastq_files = [
            str(file)
            for file in utrace.input_files.get_path_objects_by_uftype(
                urgap.uftypes.transcriptomics.reads.FASTQ_GZ,
            )
        ]
        utrace.urun_dict.command_list.append(str(self.exe_path))
        utrace.urun_dict.command_list.append("quant")
        utrace.urun_dict.command_list.append(
            f"--index={utrace.input_files.get_path_objects_by_uftype(urgap.uftypes.transcriptomics.KALLISTO_INDEX)[0]}",
        )
        utrace.urun_dict.command_list.append(
            f"--output={utrace.output_files[0].path.parent}",
        )
        for k, v in utrace.urun_dict.items():
            utrace.urun_dict.command_list.extend([k, v])
        utrace.urun_dict.command_list.extend(fastq_files)
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for KallistoQuant wrapper.

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
        """Postflight routine for KallistoQuant wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        (utrace.output_files[0].path.parent / "abundance.tsv").rename(
            utrace.output_files[0].path,
        )
        return utrace