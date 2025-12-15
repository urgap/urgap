"""Urgap StarIndex wrapper."""

import multiprocessing as mp
import zipfile

from zipfile import ZipFile

import urgap


class StarIndex(urgap.unode.UNodeBase):
    """Urgap wrapper for the StarIndex read aligner."""

    META_INFO = {
        "name": "StarIndex",
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
        """Initialize StarIndex class."""
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
        for k, v in utrace.urun_dict.items():
            utrace.urun_dict.command_list.extend([k, v])
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for StarIndex wrapper.

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
        """Postflight routine for StarIndex wrapper.

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

        # Zip the meta info files
        meta_info_files = list(outputs.glob("*.txt")) + list(outputs.glob("*.tab"))
        meta_info_zip_path = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.STAR_2_INDEX_META_ZIP,
        )[0]
        with ZipFile(meta_info_zip_path, "w", zipfile.ZIP_DEFLATED) as file:
            for meta_file in meta_info_files:
                file.write(meta_file, arcname=meta_file.name)

        return utrace