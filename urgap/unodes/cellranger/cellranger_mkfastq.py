"""Urgap CellrangerMkfastq wrapper."""

import logging
import os
import tarfile
import xml.etree.ElementTree as ET

from pathlib import Path

import tqdm

import urgap

logger = logging.getLogger(__name__)


class CellrangerMkfastq(urgap.unode.UNodeBase):
    """Urgap wrapper for CellrangerMkfastq."""

    META_INFO = {
        "name": "CellrangerMkfastq",
        "wrapper_version": {"major": 1, "minor": 0, "patch": 0},
        "versions": [
            {"version": "8.0.1", "exe_path": "$cellranger"},
        ],
        "parameters_not_triggering_rerun": [],
        "input_uftypes": {
            urgap.uftypes.transcriptomics.cellranger.NOVASEQ_INPUT_TAR: {
                "min": 1,
                "max": 1,
            },
        },
        "output_uftypes": {
            urgap.uftypes.transcriptomics.cellranger.MKFASTQ_OUTPUT_TAR: {
                "min": 1,
                "max": 1,
            },
        },
        "engine": None,
        "engine_type": ("transcriptomics",),
        "citation": """
        Zheng, G. X. Y. et al. (2017). Massively parallel digital transcriptional profiling of single cells. Nature Communications 8: 1-12, doi:10.1038/ncomms14049
        """,
    }

    def __init__(self) -> None:
        """Initialize CellrangerMkfastq class."""
        super().__init__()

    def create_command_list(
        self,
        utrace: urgap.UTrace,
        input_folder: Path,
        samplesheet: Path,
    ) -> urgap.UTrace:
        """Create the command list from input parameters.

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.
            input_folder: Path to the input folder.
            samplesheet: Path to the Samplesheet.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        utrace.urun_dict.command_list = [str(self.exe_path)]
        utrace.urun_dict.command_list.append("mkfastq")
        utrace.urun_dict.command_list.append(f"--run={input_folder!s}")
        utrace.urun_dict.command_list.append(f"--samplesheet={samplesheet!s}")

        for translated_dict in utrace.urun_dict.translations["all_params"].values():
            translated_dict_key = translated_dict["translated_key"]
            translated_dict_value = translated_dict["translated_value"]
            if translated_dict_key in [
                "--jobmode",
            ]:
                utrace.urun_dict.command_list.append(
                    f"{translated_dict_key}={translated_dict_value!s}",
                )
        for k, v in utrace.urun_dict.parameters.items():
            utrace.urun_dict.command_list.append(f"{k}={v}")
        return utrace

    def preflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Preflight routine for CellrangerMkfastq wrapper.

        During preflight,
            - input tars are untared
            - command list is composed

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        cellranger_tar_path = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.cellranger.NOVASEQ_INPUT_TAR,
        )[0]
        untar_scratch_path = cellranger_tar_path.parent / "uncompressed_tar"
        untarred_paths = _untar_with_progress(cellranger_tar_path, untar_scratch_path)
        sample_sheet_path = next(
            p for p in untarred_paths if p.name == "SampleSheet.csv"
        )
        run_input_folder = (
            untar_scratch_path
            / untarred_paths[0].relative_to(untar_scratch_path).parts[0]
        )
        utrace = self.create_command_list(
            utrace=utrace,
            input_folder=run_input_folder,
            samplesheet=sample_sheet_path,
        )
        os.chdir(urgap.scratch_disk_base)
        return utrace

    def postflight(
        self,
        utrace: urgap.UTrace,
    ) -> urgap.UTrace:
        """Postflight routine for CellrangerMkfastq wrapper.

        During postflight,
            - output tar is generated

        Args:
            utrace: Combination of urun_dict, ufile_list and unode.meta.

        Returns:
            UTrace object, combination of urun_dict, ufile_list and unode.meta.
        """
        cellranger_tar_path = utrace.input_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.cellranger.NOVASEQ_INPUT_TAR,
        )[0]
        untar_scratch_path = cellranger_tar_path.parent / "uncompressed_tar"
        run_input_folder = next(untar_scratch_path.glob("*/"))
        tree = ET.parse(f"{run_input_folder}/RunParameters.xml")
        element_path = "./RfidsInfo/FlowCellSerialBarcode"
        root = tree.getroot()
        e = root.find(element_path)
        flowcell_id = e.text
        msg = f"Flowcell ID = {flowcell_id}"
        logger.info(msg)
        cellranger_output = (
            urgap.scratch_disk_base / flowcell_id / "outs" / "fastq_path"
        )
        output_tar_path = utrace.output_files.get_path_objects_by_uftype(
            urgap.uftypes.transcriptomics.cellranger.MKFASTQ_OUTPUT_TAR,
        )[0]
        logger.info("Taring output.")
        msg = f"Output tar path = {output_tar_path}"
        logger.info(msg)
        with tarfile.open(output_tar_path, mode="w:") as file:
            file.add(
                cellranger_output,
                arcname=flowcell_id,
            )
        utrace.output_files[0].tags["flowcell_id"] = flowcell_id
        return utrace


def _untar_with_progress(tar_path: str | Path, extract_path: str | Path) -> list:
    total_size = Path(tar_path).stat().st_size
    tar_files = []
    with (
        tar_path.open("rb") as f,
        tqdm.tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc="Untarring mkfastq input",
        ) as pbar,
        tarfile.open(fileobj=f) as tar,
    ):
        for member in tar:
            tar_files.append(extract_path / member.name)
            tar.extract(member, path=extract_path)
            pbar.update(member.size)
    return tar_files
