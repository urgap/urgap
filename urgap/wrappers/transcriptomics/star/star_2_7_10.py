"""Urgap star_2_7_10 wrapper."""

import logging
import multiprocessing as mp
import os

from zipfile import ZipFile

import urgap


class star_2_7_10(urgap.unode.UNodeBase):
    """Urgap wrapper for the star 2.7.10 read aligner."""

    META_INFO = {
        "name": "star_2_7_10",
        "version": "2.7.10",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "release_date": "15.01.2022",
        "api_port": 42915,
        "engine_type": ("aligner", "ngs"),
        "platform_independent": False,
        "utranslation_style": "star_style_1",
        "engine": {
            "darwin": {
                "arm64": {
                    "exe": "STAR",
                    "uri": None,
                    "urn": "darwin/arm64/star_2_7_10.zip",
                    "external_md5": "0a56bf6570d36ef412701240c48451cc",
                    "external_url": "https://github.com/alexdobin/STAR/releases/download/2.7.10a_alpha_220207/STAR_MacOSX_x86_64.zip",
                },
                "x86_64": {
                    "exe": "STAR",
                    "uri": None,
                    "urn": "darwin/x86_64/star_2_7_10.zip",
                    "external_md5": "0a56bf6570d36ef412701240c48451cc",
                    "external_url": "https://github.com/alexdobin/STAR/releases/download/2.7.10a_alpha_220207/STAR_MacOSX_x86_64.zip",
                },
            },
            "linux": {
                "arm64": {
                    "exe": "STAR",
                    "uri": None,
                    "urn": "linux/arm64/star_2_7_10.zip",
                    "urn_md5": "3ac2265444e610e443a73f2fc55bbdf7",
                    "external_md5": "1907933cd877d6ae158e57c206fa2b15",
                    "external_url": "https://github.com/alexdobin/STAR/releases/download/2.7.10a_alpha_220207/STAR_Linux_x86_64_static.zip",
                },
                "x86_64": {
                    "exe": "STAR",
                    "uri": None,
                    "urn": "linux/x86_64/star_2_7_10.zip",
                    "urn_md5": "3ac2265444e610e443a73f2fc55bbdf7",
                    "external_md5": "1907933cd877d6ae158e57c206fa2b15",
                    "external_url": "https://github.com/alexdobin/STAR/releases/download/2.7.10a_alpha_220207/STAR_Linux_x86_64_static.zip",
                },
            },
        },
        "input_uftypes": {
            urgap.uftypes.transcriptomics.STAR_2_INDEX: {"min": 3, "max": 3},
            urgap.uftypes.transcriptomics.STAR_2_INDEX_META_ZIP: {"min": 1, "max": 1},
            urgap.uftypes.transcriptomics.reads.FASTQ_GZ: {"min": 1, "max": -1},
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.reads.SAM: {"min": 1, "max": 1},
            urgap.uftypes.transcriptomics.STAR_2_QUANT_TSV: {"min": 0, "max": 1},
        },
        "citation": """
        Dobin, A., Davis, C. A., Schlesinger, F., Drenkow, J., Zaleski, C., Jha, S., Batut, P., Chaisson, M., & Gingeras, T. R. (2013). STAR: ultrafast universal RNA-seq aligner.
        Bioinformatics (Oxford, England), 29(1), 15-21. https://doi.org/10.1093/bioinformatics/bts635
        """,
    }

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Initialize star_2_7_10 class."""
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
        fastq_files = []
        fastq_gz_indices = utrace.input_files.get_indices_by_uftype(
            uftype=urgap.uftypes.transcriptomics.reads.FASTQ_GZ,
        )
        for i in fastq_gz_indices:
            uncompressed_fastq_path = str(utrace.input_files[i].uncompress()[0].path)
            fastq_files.append(uncompressed_fastq_path)

        utrace.urun_dict.command_list.append(str(self.exe_path))

        utrace.urun_dict.command_list.append("--readFilesIn")
        utrace.urun_dict.command_list.extend(fastq_files)
        utrace.urun_dict.command_list.append("--genomeDir")
        utrace.urun_dict.command_list.append(
            str(
                utrace.input_files.get_path_objects_by_uftype(
                    urgap.uftypes.transcriptomics.STAR_2_INDEX,
                )[0].parent,
            ),
        )
        utrace.urun_dict.command_list.append("--outFileNamePrefix")
        utrace.urun_dict.command_list.append(
            str(utrace.output_files[0].path.parent) + "/",
        )
        for value in utrace.urun_dict.translations["all_params"].values():
            if len(value["translated_key"]) != 0:
                utrace.urun_dict.command_list.append(value["translated_key"])
                if (value["original_key"] == "cpus") and (
                    value["translated_value"] == -1
                ):
                    value["translated_value"] = mp.cpu_count() - 1
            values = str(value["translated_value"])
            for v in values.split(" "):
                utrace.urun_dict.command_list.append(v)

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for star_2_7_10 wrapper.

        During preflight,
            - parameters are formatted
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        index_files = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.STAR_2_INDEX,
        )
        legacy_names = ("Genome", "SA", "SAindex")
        for legacy_name, index_file in zip(
            legacy_names,
            index_files,
            strict=False,
        ):
            legacy_file = index_file.parent / legacy_name
            if legacy_file.exists():
                logging.info("Removing symbolic links from previous run")
                os.unlink(legacy_file)
            os.symlink(index_file, legacy_file)

        meta_zip = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.STAR_2_INDEX_META_ZIP,
        )[0]
        with ZipFile(meta_zip, "r") as z_file:
            z_file.extractall(path=index_files[0].parent)
        return self.create_command_list(utrace=utrace)

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for star_2_7_10 wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        os.rename(
            utrace.output_files[0].path.parent / "Aligned.out.sam",
            utrace.output_files[0].path,
        )
        quant_tab = utrace.output_files[0].path.parent / "SJ.out.tab"
        if quant_tab.exists() is True:
            utrace.extend_output_files_by_uftype(
                uftype=urgap.uftypes.transcriptomics.STAR_2_QUANT_TSV,
            )
            os.rename(quant_tab, utrace.output_files[-1].path)
        return utrace
