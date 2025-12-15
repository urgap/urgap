"""Urgap Star wrapper."""

import logging
import multiprocessing as mp

from zipfile import ZipFile

import urgap


class Star(urgap.unode.UNodeBase):
    """Urgap wrapper for the Star read aligner.

    https://github.com/alexdobin/STAR/releases
    """

    META_INFO = {
        "name": "Star",
        "versions": [
            {
                "version": "2.7.11",
                "exe_path": "$STAR",
            },
        ],
        "parameters_not_triggering_rerun": ["--runThreadN"],
        "engine": None,
        "engine_type": ("aligner", "ngs"),
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
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
        """Initialize Star class."""
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
        if "--runThreadN" not in utrace.urun_dict:
            utrace.urun_dict.command_list.extend(
                ["--runThreadN", str(mp.cpu_count() - 1)],
            )
        for k, v in utrace.urun_dict.items():
            utrace.urun_dict.command_list.extend([k, v])

        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for Star wrapper.

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
                legacy_file.unlink()
            index_file.symlink_to(legacy_file)

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
        """Postflight routine for Star wrapper.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        (utrace.output_files[0].path.parent / "Aligned.out.sam").rename(
            utrace.output_files[0].path,
        )
        quant_tab = utrace.output_files[0].path.parent / "SJ.out.tab"
        if quant_tab.exists() is True:
            utrace.extend_output_files_by_uftype(
                uftype=urgap.uftypes.transcriptomics.STAR_2_QUANT_TSV,
            )
            quant_tab.rename(utrace.output_files[-1].path)
        return utrace