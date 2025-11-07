"""Urgap star_index_2_7_10 wrapper."""

import multiprocessing as mp
import os
import zipfile

from zipfile import ZipFile

import urgap


class star_index_2_7_10(urgap.unode.UNodeBase):
    """Urgap wrapper for the star 2.7.10 read aligner."""

    META_INFO = {
        "name": "star_index_2_7_10",
        "version": "2.7.10",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "15.01.2022",
        "api_port": 42916,
        "engine_type": ("aligner", "ngs"),
        "platform_independent": False,
        "utranslation_style": "star_index_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "STAR",
                    "uri": None,
                    "urn": "darwin/arm64/star_index_2_7_10.zip",
                    "urn_md5": "0a56bf6570d36ef412701240c48451cc",
                    "external_md5": "0a56bf6570d36ef412701240c48451cc",
                    "external_url": "https://github.com/alexdobin/STAR/releases/download/2.7.10a_alpha_220207/STAR_MacOSX_x86_64.zip",
                },
                "x86_64": {
                    "exe": "STAR",
                    "uri": None,
                    "urn": "darwin/x86_64/star_index_2_7_10.zip",
                    "urn_md5": "0a56bf6570d36ef412701240c48451cc",
                    "external_md5": "0a56bf6570d36ef412701240c48451cc",
                    "external_url": "https://github.com/alexdobin/STAR/releases/download/2.7.10a_alpha_220207/STAR_MacOSX_x86_64.zip",
                },
            },
            "linux": {
                "arm64": {
                    "exe": "STAR",
                    "uri": None,
                    "urn": "linux/arm64/star_index_2_7_10.zip",
                    "urn_md5": "c49706ee7e586d4c5a99d528bbb76200",
                    "external_md5": "1907933cd877d6ae158e57c206fa2b15",
                    "external_url": "https://github.com/alexdobin/STAR/releases/download/2.7.10a_alpha_220207/STAR_Linux_x86_64_static.zip",
                },
                "x86_64": {
                    "exe": "STAR",
                    "uri": None,
                    "urn": "linux/x86_64/star_index_2_7_10.zip",
                    "urn_md5": "c49706ee7e586d4c5a99d528bbb76200",
                    "external_md5": "1907933cd877d6ae158e57c206fa2b15",
                    "external_url": "https://github.com/alexdobin/STAR/releases/download/2.7.10a_alpha_220207/STAR_Linux_x86_64_static.zip",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.transcriptomics.GTF: {"min": 0, "max": 1},
            urgap.uftypes.transcriptomics.FASTA: {"min": 1, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.STAR_2_INDEX: {"min": 3, "max": 3},
            urgap.uftypes.transcriptomics.STAR_2_INDEX_META_ZIP: {"min": 1, "max": 1},
        },
        "citation": """
        Dobin, A., Davis, C. A., Schlesinger, F., Drenkow, J., Zaleski, C., Jha, S., Batut, P., Chaisson, M., & Gingeras, T. R. (2013). STAR: ultrafast universal RNA-seq aligner.
        Bioinformatics (Oxford, England), 29(1), 15-21. https://doi.org/10.1093/bioinformatics/bts635
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize star_index_2_7_10 class."""
        super().__init__(*args, **kwargs)

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
        fasta_files = [
            str(file)
            for file in utrace.input_files.get_path_objects_by_uftype(
                urgap.uftypes.transcriptomics.FASTA,
            )
        ]

        utrace.urun_dict.command_list.append(str(self.exe_path))

        utrace.urun_dict.command_list.append("--runMode")
        utrace.urun_dict.command_list.append("genomeGenerate")
        utrace.urun_dict.command_list.append("--genomeFastaFiles")
        utrace.urun_dict.command_list.extend(fasta_files)
        utrace.urun_dict.command_list.append("--genomeDir")
        utrace.urun_dict.command_list.append(str(utrace.output_files[0].path.parent))
        gtf_file = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.GTF,
        )
        if len(gtf_file) == 1:
            utrace.urun_dict.command_list.append("--sjdbGTFfile")
            utrace.urun_dict.command_list.append(str(gtf_file[0]))

        for value in utrace.urun_dict.translations["all_params"].values():
            if len(value["translated_key"]) != 0:
                utrace.urun_dict.command_list.append(value["translated_key"])
                if (value["original_key"] == "cpus") and (
                    value["translated_value"] == -1
                ):
                    value["translated_value"] = mp.cpu_count() - 1
            utrace.urun_dict.command_list.append(str(value["translated_value"]))

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for star_index_2_7_10 wrapper.

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
        """Postflight routine for star_index_2_7_10 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        outputs = utrace.output_files[0].path.parent
        index_files = list(set(outputs.glob("*")) - set(outputs.glob("*.*")))
        index_files.sort()
        output_index_files = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.STAR_2_INDEX,
        )
        for i, index_file in enumerate(index_files):
            new_name = str(output_index_files[i])
            os.rename(str(index_file), new_name)

        # Zip the meta info files
        meta_info_files = list(outputs.glob("*.txt")) + list(outputs.glob("*.tab"))
        meta_info_zip_path = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.STAR_2_INDEX_META_ZIP,
        )[0]
        with ZipFile(meta_info_zip_path, "w", zipfile.ZIP_DEFLATED) as file:
            for meta_file in meta_info_files:
                file.write(meta_file, arcname=meta_file.name)

        return utrace
